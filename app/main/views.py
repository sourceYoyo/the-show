# coding: utf-8
from flask import Flask,render_template


from . import main
from .data import getFlows,report_index,getAnay,getWebs,getBasicFlows,getWa3fCompare,getFlows


@main.route('/index')
@main.route('/')
def get_index():
    flows = getFlows()
    web_titles,web_series,vuls = report_index()
    hots,danger_hots,dangers,dh = getWebs()     
    compare = getWa3fCompare()
    app_series,protocal_series = getFlows()
    return render_template('index.html',flows=flows,app_series = app_series,protocal_series = protocal_series,
    web_titles=web_titles,web_series=web_series,vuls=vuls,hots=hots[:5],dangers=dangers[:5],compare=compare)


@main.route('/flow')
@main.route('/')
def get_flow():
    flows = getBasicFlows()
    hots,danger_hots,dangers_in,dangers_out = getWebs()     
    return render_template('flow.html',flows=flows,danger_hots=danger_hots,dangers_in=dangers_in,hots=hots,dangers_out=dangers_out)



@main.route('/ivre')
@login_required
def ivre():
    return render_template('ivre.html')

@main.route('/anay')
@login_required
def anay():
    port_revolve_dates,port_stable_data,port_newest_data=getAnay() 
    #[],[],[]
    

    return render_template('anay.html',port_newest_data=port_newest_data,port_stable_data=port_stable_data,port_revolve_dates=port_revolve_dates)


    
@main.route('/posts')
@login_required
def posts():
    total_count_bugs, total_count_posts = get_total_count()
    page = int(request.args.get('page', 1))
    if page < 1:
        page = 1
    keywords=''
    search_by_html=False
    content_search_by='by_posts'
    page_info = search_mongodb(keywords, page, content_search_by, search_by_html)
    return render_template('app.html', total_count_posts=total_count_posts,page_info=page_info,title=u'清华大学校园网渗透测试',type='posts')

@main.route('/reports')
@login_required
def bugs():
    total_count_bugs, total_count_posts = get_total_count()
    page = int(request.args.get('page', 1))
    if page < 1:
        page = 1
    keywords=''
    search_by_html=False
    content_search_by='by_bugs'
    page_info = search_mongodb_reports(keywords, page, content_search_by, search_by_html)
    return render_template('reports.html',  total_count_posts=total_count_bugs,page_info=page_info,title=u'清华大学校园网渗透测试',type='bugs')

@main.route('/report')
@login_required
def bug_detail():
    id = request.args.get('id')
    target = request.args.get('target')
    #post=search_bug(ObjectId(id))
    post=search_report(target)[0]
    vuls = post['vuls']
    for i in range(len(vuls)):
        vuls[i]['id']=i
    post['vuls'] = vuls
    return render_template('report.html',post=post)

@main.route('/report/edit',methods=["POST"])
@login_required
def bug_edit():
    description = request.form['description']     
    target = request.form['target'][:-2]  
    _id = request.form['_id']  
    updateReport(_id,target,description)
    return redirect('/report?target='+target)

@main.route('/posts/search')
@login_required
def post_search():
    return search('by_posts','search_posts.html',True)

@main.route('/reports/search')
@login_required
def bug_search():
    return search('by_bugs','search_bugs.html',False)

def search(content_search_by,TEMPLATE_NAME,notreport):
    keywords = request.args.get('keywords')
    if keywords==None:
        keywords = ''
    page = int(request.args.get('page', 1))
    '''search_by_html = True if 'true' == request.args.get(
        'search_by_html', 'false').lower() else False    '''
    search_by_html = False        
    if page < 1:
        page = 1    
    if notreport:
        page_info = search_mongodb(keywords, page, content_search_by, search_by_html)
    else:
        page_info = search_mongodb_reports(keywords, page, content_search_by, search_by_html)
    return render_template(TEMPLATE_NAME, keywords=keywords, page_info=page_info, search_by_html=search_by_html, title=u'thu-渗透测试')
