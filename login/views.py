from django.shortcuts import render
from django.shortcuts import redirect
import json
import re
import os
from itertools import chain

from django.core import serializers
from django.http import HttpResponse, HttpResponseRedirect
from django.db import connection
from django.http import FileResponse

from django.http import JsonResponse

from . import models
# Create your views here.
from django.views.decorators.csrf import csrf_exempt

num_per = 5
#####
dia_starts = models.RawText.objects.filter(sentence_id=1)
num_dia = dia_starts.count()
dia_ids = [m.example_id for m in dia_starts]

# bio_dict = {0:'0:O',1:'1:I',2:'2:B-症状',3:'3:B-药品名',4:'4:B-药物类别',
#     5:'5:B-服用方式等',6:'6:B-检查',7:'7:B-操作',8:'8:B-注意事项'}

# act_dict = {1:'症状',2:'基本信息',3:'已有检查和治疗',4:'用药建议',
# 5:'就医建议',6:'注意事项',7:'其他'}


sections1 = models.LabelClass.objects.all()
bio_dict = {}
res1 = []
for i in sections1:
    bio_dict[i.labelid] = i.labelmeaning
    res1.append([i.labelid, i.labelmeaning])

sections2 = models.ActClass.objects.all()
act_dict = {}
res2 = []
for i in sections2:
    act_dict[i.aid] = i.actid
    res2.append([i.aid, i.actid])


def taghome(request):
    return redirect('/login/')


def index(request):
    if request.session.get('is_login', None):
        reviewerid = request.session['userid']
        print('reviewerid:', reviewerid)
        lasttext = models.TagText.objects.filter(reviewer=reviewerid).order_by('-savedate')

        userstart = models.User.objects.get(id=reviewerid).start
        userend = models.User.objects.get(id=reviewerid).end
        start_index = dia_ids.index(userstart)
        end_index = dia_ids.index(userend)
        text_exist = lasttext.exists()
        if text_exist:
            unique_list = models.TagText.objects.filter(reviewer=reviewerid, sentence_id=1).order_by('savedate').values(
                'unique_id')
            complete_text = len(list(unique_list))
            total_text = end_index - start_index + 1
            complete_percent = int((complete_text / total_text) * 100)
            undo_text = end_index - start_index - complete_text + 1
            undo_percent = int((undo_text / total_text) * 100)
            return render(request, 'index.html',
                          {'complete': complete_text, 'percent1': complete_percent, 'undo': undo_text,
                           'percent2': undo_percent})
        else:
            last_textid = 0
            undo_text = end_index - start_index + 1
            complete_percent = 0
            undo_percent = 100
            return render(request, 'index.html',
                          {'complete': last_textid, 'percent1': complete_percent, 'undo': undo_text,
                           'percent2': undo_percent})

    else:
        message = "您尚未登陆！"
        return render(request, 'page-login.html', {'message': message})


def example1(request):
    if request.session.get('is_login', None):
        return render(request, 'example1.html')
    else:
        message = "您尚未登录！"
        return render(request, 'page-login.html', {'message': message})


def example2(request):
    if request.session.get('is_login', None):
        return render(request, 'example2.html')
    else:
        message = "您尚未登录！"
        return render(request, 'page-login.html', {'message': message})


def example3(request):
    if request.session.get('is_login', None):
        return render(request, 'example3.html')
    else:
        message = "您尚未登录！"
        return render(request, 'page-login.html', {'message': message})


def taglogistic(request):
    if request.session.get('is_login', None):
        filepath = '/home/LT/fraudsite/login/templates/taglogistic.pdf'
        file = open(filepath, 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="taglogistic.pdf"'
        return response
    else:
        message = "您尚未登录！"
        return render(request, 'page-login.html', {'message': message})


@csrf_exempt
def login(request):
    if request.session.get('is_login', None):  # 不允许重复登录
        return redirect('/index/')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username.strip() and password:  # 用户名和密码非空
            try:
                print('username:', username)
                user = models.User.objects.get(name=username)
            except:
                message = '用户不存在！'
                return render(request, 'page-login.html', {'message': message})

            if user.password == password:
                # print(username, password)
                request.session.set_expiry(0)
                request.session['is_login'] = True
                request.session['userid'] = user.id
                request.session['username'] = user.name
                request.session['userstart'] = user.start
                request.session['userend'] = user.end
                return redirect("/index/")

            else:
                message = '密码不正确！'
                return render(request, 'page-login.html', {'message': message})
        else:
            message = '用户名和密码不能为空'
            return render(request, 'page-login.html', {'message': message})
    return render(request, 'page-login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username.strip() and password:
            same_name_user = models.User.objects.filter(name=username)
            if same_name_user:
                message = '用户名已经存在'
                return render(request, 'page-register.html', {'message': message})

            # 注册时即分配

            users = models.User.objects.all()
            user_len = users.count()

            if num_dia > num_per * user_len:
                start = dia_ids[num_per * user_len]  # start and end both included
                if num_dia > (num_per * user_len + num_per - 1):
                    end = dia_ids[num_per * user_len + num_per - 1]
                else:
                    end = dia_ids[num_dia - 1]
            else:
                message = '当前待标注样本已分配完毕，请联系管理员！'
                return render(request, 'page-register.html', {'message': message})

            new_user = models.User()
            new_user.name = username
            new_user.password = password
            new_user.start = start
            new_user.end = end

            new_user.save()
            return redirect("/login/")
        else:
            return render(request, 'page-register.html')
    return render(request, 'page-register.html')


def logout(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    request.session.flush()
    return redirect("/login/")


def check_report(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    reviewerid = request.session['userid']
    lasttext = models.TagText.objects.filter(reviewer=reviewerid).order_by('-textid')
    text_exist = lasttext.exists()
    if not text_exist:  # 尚未开始标注
        message = "您尚未开始标注!"
        return render(request, 'check.html', {'message': message})
    else:
        message = "您标注过以下文本："
        textlist = models.TagText.objects.filter(reviewer=reviewerid, sentence_id=1)
        example_ids = [i.example_id for i in textlist]
        reports = [i.report for i in textlist]
        tagged = zip(example_ids, reports)

        return render(request, 'check1.html', {'tagged': tagged, 'message': message})


def check(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    reviewerid = request.session['userid']
    lasttext = models.TagText.objects.filter(reviewer=reviewerid).order_by('-textid')
    text_exist = lasttext.exists()
    if not text_exist:  # 尚未开始标注
        message = "您尚未开始标注!"
        return render(request, 'check.html', {'message': message})
    else:  # 已有标注记录
        message = "您标注过以下文本："
        textlist = models.TagText.objects.filter(reviewer=reviewerid,
                                                 sentence_id=1)  # .order_by('savedate').values('sentence')
        example_ids = [i.example_id for i in textlist]
        # unique_ids = [i.unique_id for i in textlist]
        questions = [models.SelfReport.objects.get(example_id=i).question for i in example_ids]
        diagnoses = [models.SelfReport.objects.get(example_id=i).diagnose for i in example_ids]

        tagged = zip(example_ids, questions, diagnoses)

        return render(request, 'check.html', {'tagged': tagged, 'message': message})


@csrf_exempt
def lookandmodify1(request):
    # print('******************8')
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")

    # example_id = request.POST.get('textid', None)

    if request.is_ajax():
        example_id = request.POST.get('textid', None)
        # print('example_id:',example_id)
        uid = example_id + '_1'
        modify = request.POST.get('modify', None)

    reviewerid = request.session['userid']

    search_dict = dict()
    if example_id:
        search_dict['example_id'] = example_id
    if reviewerid:
        search_dict['reviewer'] = reviewerid

    tag_info = models.TagText.objects.filter(example_id=example_id, reviewer=reviewerid)

    tag_sum_1 = [SumOfSentence(tag) for tag in tag_info]

    len_bio_dict = len(bio_dict)

    tag_sum = [list(chain(*([sum[j] for sum in tag_sum_1]))) for j in range(len_bio_dict)]

    tag_sum = [list(set(li)) for li in tag_sum]
    tag_sum_1 = []
    for i in range(2, len_bio_dict):
        s = bio_dict[i][4:]
        if tag_sum[i] != []:
            s = s + '：' + '，'.join(tag_sum[i])
        else:
            s = s + '：' + '（空）'
        tag_sum_1.append(s)

    dia_text = []
    for i in tag_info:
        try:
            add_s = i.speaker + ':' + i.sentence
        except:
            add_s = i.speaker + ':' + '(空)'
        dia_text.append(add_s)

    selfreport = models.SelfReport.objects.get(example_id=example_id).question
    diagnose = models.SelfReport.objects.get(example_id=example_id).diagnose
    exist_report = models.TagText.objects.get(example_id=example_id, sentence_id=1, reviewer=reviewerid).report

    return render(request, 'modify1.html', {'dia_text': dia_text, 'selfreport': selfreport,
                                            'diagnose': diagnose, 'nowtext_id': example_id, 'tag_sum': tag_sum_1,
                                            'exist_report': exist_report})


@csrf_exempt
def lookandmodify(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")

    eid = request.POST.get('eid', None)

    reviewer = request.session['userid']

    TagData = models.TagText.objects.filter(example_id=eid, reviewer=reviewer)
    cutted_text = [i.sentence for i in TagData]  # cutsent(nowtext)
    people = [i.speaker for i in TagData]
    uid = [i.unique_id for i in TagData]

    label = []
    dia_text = []
    for i in TagData:
        try:
            add_ = list(i.label)
            add_s = i.speaker + ':' + i.sentence
        except:
            add_ = []
            add_s = i.speaker + ':' + '(空)'
        label.append(add_)
        dia_text.append(add_s)

    dia_text = zip(dia_text)

    lenpos = [dict(zip(range(1, len(i) + 1), [bio_dict[int(j)] for j in i])) for i in label]

    acts = [i.dialogue_act for i in TagData]
    norms = []
    for i in TagData:
        norm0 = i.normalized.split('|')[:-1]
        norms.append(dict(zip(range(1, len(norm0) + 1), norm0)))

    cutted = zip(uid, cutted_text, people, acts, lenpos, norms)

    selfreport = models.SelfReport.objects.get(example_id=eid).question
    diagnose = models.SelfReport.objects.get(example_id=eid).diagnose

    return render(request, 'modify_new.html', {'dia_text': dia_text, 'selfreport': selfreport, 'diagnose': diagnose,
                                               'nowtext_id': eid, 'cutted': cutted, 'sections_BIO': res1,
                                               'sections_ACT': res2, 'lenpos': lenpos})


@csrf_exempt
def tagging(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")

    # 先确定标注用户，此时标注内容
    reviewerid = request.session['userid']
    # print('reviewerid:',reviewerid)
    lasttext = models.TagText.objects.filter(reviewer=reviewerid, sentence_id=1).order_by('-savedate')
    text_exist = lasttext.exists()

    userstart = models.User.objects.get(id=reviewerid).start
    topid = models.User.objects.get(id=reviewerid).end  # end 是example_id

    # 判断该用户是否已有标注记录。
    # 如果没有，则从start开始标注。
    # 如果有，判断是否ajax，如果是，则接着last_textid从POST.get 获得；如果不是，last_texid从lasttext获得
    # 判断是否标注任务全部完成。
    # 如果
    if not text_exist:  # 尚未开始标注
        now_id = userstart

    else:  # 已有标注记录
        # 得到已标记的exampid 在 dia_act 中的index
        id_exist = [i.example_id for i in lasttext]
        # for text in lasttext:
        #     eid = int(text.example_id)
        #     id_exist.append(eid)
        # id_exist = set(id_exist) # 选择出有bio标记的
        id_exist_set = set(id_exist)
        id_all = [i for i in dia_ids[dia_ids.index(userstart): dia_ids.index(topid) + 1]]
        id_no = []
        for eid in id_all:
            if eid not in id_exist_set:
                id_no.append(eid)

        if id_no != []:
            now_id = id_no[0]

        else:
            return render(request, 'tag.html', {'nowtext_id': '您已完成全部标注任务！'})

    nowtext0 = models.RawText.objects.filter(example_id=now_id)
    cutted_text = [i.sentence for i in nowtext0]  # cutsent(nowtext)
    people = [i.speaker for i in nowtext0]
    uid = [i.unique_id for i in nowtext0]

    label = []
    dia_text = []
    for i in nowtext0:
        try:
            add_ = list(i.label)
            add_s = i.speaker + ':' + i.sentence
        except:
            add_ = []
            add_s = i.speaker + ':' + '(空)'
        label.append(add_)
        dia_text.append(add_s)

    dia_text = zip(dia_text)

    lenpos = [dict(zip(range(1, len(i) + 1), [bio_dict[int(j)] for j in i])) for i in label]

    acts = ['请选择动作' for i in nowtext0]
    cutted = zip(uid, cutted_text, people, acts, lenpos)

    selfreport = models.SelfReport.objects.get(example_id=now_id).question
    diagnose = models.SelfReport.objects.get(example_id=now_id).diagnose
    return render(request, 'tag.html', {'dia_text': dia_text, 'selfreport': selfreport, 'diagnose': diagnose,
                                        'nowtext_id': now_id, 'cutted': cutted, 'sections_BIO': res1,
                                        'sections_ACT': res2, 'lenpos': lenpos})


@csrf_exempt
def savereport(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    userid = request.session['userid']

    if request.is_ajax():
        # print('****************************is_ajax')
        nowtextid = request.POST.get('nowtextid', None)
        text = request.POST.get('WReport', 1)

        search_dict = dict()
        if nowtextid:
            search_dict['unique_id'] = nowtextid + '_1'
        # if sentid:
        #     search_dict['sentence_id'] = sentid
        if userid:
            search_dict['reviewer'] = userid

        taged = models.TagText.objects.get(**search_dict)

        taged.report = text
        taged.save()
        return HttpResponse(json.dumps({"msg": 'success'}))

    else:
        print('wrong,not ajax')

        return 0


def SumOfSentence(tag):
    tag_sum = [[] for row in range(len(bio_dict))]
    label = tag.label
    sentence = tag.sentence
    n = len(label)
    i = 0
    while i < n:
        l = 1
        if (label[i] != '0') and (label[i] != '1'):
            while (i + l < n) and (label[i + l] == '1'):
                l = l + 1
            word = sentence[i:i + l]
            tag_sum[int(label[i])].append(word)
        i = i + l
    return tag_sum


@csrf_exempt
def report(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    reviewerid = request.session['userid']
    if request.is_ajax():
        data = request.POST
        example_id = request.POST.get('textid', None)
        # print('example_id:',example_id)

    else:
        # 先确定标注用户，此时标注内容

        lasttext = models.TagText.objects.filter(reviewer=reviewerid, sentence_id=1).order_by('-savedate')
        text_exist = lasttext.exists()
        userstart = models.User.objects.get(id=reviewerid).start
        topid = models.User.objects.get(id=reviewerid).end
        if not text_exist:
            example_id = userstart
        else:
            id_exist = []
            for text in lasttext:
                if text.report != 'report':
                    id_exist.append(text.example_id)
            id_exist = set(id_exist)  # 选择出有bio标记的

            id_all = set([i for i in dia_ids[dia_ids.index(userstart): dia_ids.index(topid) + 1]])
            id_no = id_all - id_exist

            id_no = list(id_no)
            # print('id_no:',id_no)
            if id_no != []:
                example_id = id_no[0]
            else:
                return render(request, 'report.html', {'nowtext_id': '您已完成所有诊疗报告！'})

    search_dict = dict()
    if example_id:
        search_dict['example_id'] = example_id
    if reviewerid:
        search_dict['reviewer'] = reviewerid

    raw_info = models.RawText.objects.filter(example_id=example_id)
    tag_info = models.TagText.objects.filter(example_id=example_id, reviewer=reviewerid)

    tag_sum_1 = [SumOfSentence(tag) for tag in tag_info]

    len_bio_dict = len(bio_dict)

    tag_sum = [list(chain(*([sum[j] for sum in tag_sum_1]))) for j in range(len_bio_dict)]

    tag_sum = [list(set(li)) for li in tag_sum]
    tag_sum_1 = []
    for i in range(2, len_bio_dict):
        s = bio_dict[i][4:]
        if tag_sum[i] != []:
            s = s + '：' + '，'.join(tag_sum[i])
        else:
            s = s + '：' + '（空）'
        tag_sum_1.append(s)

    dia_text = []
    for i in raw_info:
        try:
            add_s = i.speaker + ':' + i.sentence
        except:
            add_s = i.speaker + ':' + '(空)'
        dia_text.append(add_s)

    selfreport = models.SelfReport.objects.get(example_id=example_id).question
    diagnose = models.SelfReport.objects.get(example_id=example_id).diagnose

    return render(request, 'report.html', {'dia_text': dia_text, 'selfreport': selfreport,
                                           'diagnose': diagnose, 'nowtext_id': example_id, 'tag_sum': tag_sum_1})


def is_Chinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


def cutsent(text):
    pattern = '，|,|。|？|！|!|；|、|\s|~|……|^|-|||,|:|：|_|\?'
    test_text = text.strip()
    re_text = re.split(pattern, test_text)
    result_text = [i for i in re_text if i != '' and is_Chinese(i)]
    return result_text


@csrf_exempt
def ajaxmethod(request):
    if request.is_ajax():
        pid = request.POST.get('pid', None)
    methods = models.FraudClass.objects.filter(pid=pid)
    cid_list = []
    method_list = []
    for i in methods:
        cid_list.append(i.cid)
        method_list.append(i.method)

    leng = len(method_list)
    return HttpResponse(json.dumps({"cid": cid_list, "methods": method_list, "leng": leng}, ensure_ascii=False))


@csrf_exempt
def savetag(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    userid = request.session['userid']
    if request.is_ajax():
        nowtextid = request.POST.get('nowtextid', None)
        sentid = request.POST.get('sentid', None)
        ActBios = request.POST.get('ActBios', None)
        sen_norm = request.POST.get('sen_norm', None)

    unique_id = str(nowtextid) + '_' + sentid
    rawdata = models.RawText.objects.get(unique_id=unique_id)
    default_label = rawdata.label
    sentence = rawdata.sentence
    speaker = rawdata.speaker

    search_dict = dict()
    if nowtextid:
        search_dict['unique_id'] = unique_id
    # if sentid:
    #     search_dict['sentence_id'] = sentid
    if userid:
        search_dict['reviewer'] = userid

    user_tag_info = models.TagText.objects.filter(**search_dict)
    text_exist = user_tag_info.exists()

    # print('default:',default_label)
    # print('ActBios:',ActBios)

    label = ''

    for i in range(1, len(ActBios)):
        if ActBios[i] == '*':
            label += default_label[i - 1]
        else:
            label += ActBios[i]
    # print('label:',label)

    dialogue_act = ActBios[:1]
    normalized = sen_norm

    if text_exist:
        data = {'label': label, 'dialogue_act': dialogue_act, 'normalized': normalized}
        user_tag_info.update(**data)
    else:
        new_tag = models.TagText()
        new_tag.example_id = nowtextid
        # print('*********savetag:*********',new_tag.example_id)
        new_tag.unique_id = unique_id
        new_tag.sentence_id = sentid
        new_tag.speaker = speaker
        new_tag.sentence = sentence

        new_tag.label = label
        new_tag.normalized = normalized
        new_tag.type = ''
        if dialogue_act != '*':
            new_tag.dialogue_act = act_dict[dialogue_act]  # act_dict[int(dialogue_act)]
        else:
            new_tag.dialogue_act = '未标记'
        new_tag.report = 'report'
        new_tag.reviewer = userid
        # print('*********savetag:*********',new_tag.sentence_id, new_tag.dialogue_act)
        new_tag.save()

    return HttpResponse(json.dumps({"msg": 'success'}))


@csrf_exempt
def modify_report(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    userid = request.session['userid']

    return HttpResponse(json.dumps({"msg": 'success'}))


@csrf_exempt
def modifytag(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/login/")
    userid = request.session['userid']

    if request.is_ajax():
        example_id = request.POST.get('example_id', None)
        dialogue_act = request.POST.get('dialogue_act', None)
        Bios = request.POST.get('Bios', None)
        sen_norm = request.POST.get('sen_norm', None)
        sentence_id = request.POST.get('sentid', None)

    search_dict = dict()
    search_dict['example_id'] = example_id
    search_dict['sentence_id'] = sentence_id
    search_dict['reviewer'] = userid

    user_tag_info = models.TagText.objects.filter(**search_dict)

    normalized = sen_norm

    rawlabel = models.TagText.objects.get(**search_dict).label
    label = ''

    for i, w in enumerate(Bios):
        if w != '*':
            label += w
        else:
            label += rawlabel[i]

    data = {'label': label, 'dialogue_act': dialogue_act, 'normalized': normalized}
    user_tag_info.update(**data)

    return HttpResponse(json.dumps({"msg": 'success'}))
