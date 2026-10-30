from django.http import Http404
from django.shortcuts import render
from django.utils.translation import gettext
from . import pests


def selection(request, crop_slug=None):
    all_crops=pests.crops()
    selected=[]
    if request.user.is_authenticated:
        names=request.user.profile.selected_crops or []
        selected=[c for name in names for c in all_crops if c['name']==name]
    raw=crop_slug if crop_slug is not None else request.GET.get('crop')
    if raw is not None:
        crop=next((c for c in all_crops if c['slug']==raw),None)
        if crop is None:raise Http404('Unknown crop')
    else:
        crop=selected[0] if selected else next(c for c in all_crops if c['name']=='Tomato')
    return {'crop':crop,'saved_crops':selected,'other_crops':[c for c in all_crops if c not in selected],
            'is_saved_crop':crop['name'] in {c['name'] for c in selected}}


def index(request):
    context=selection(request)
    crop=context['crop'];query=request.GET.get('q','').strip()[:100]
    kind=request.GET.get('type','all')
    if kind not in {'all','disease','pest','disorder'}:kind='all'
    stage=request.GET.get('stage','')
    stage_choices=pests.stages(crop)
    if stage and stage not in {s['slug'] for s in stage_choices}:raise Http404('Unknown stage')
    all_issues=pests.issues_for(crop)
    rows=[r for r in all_issues if (kind=='all' or r['category']==kind) and
          (not query or query.casefold() in ' '.join([r['name'],gettext(r['name']),r['cause'],r['early']]).casefold())]
    sections=[]
    for item in stage_choices:
        if stage and stage!=item['slug']:continue
        entries=[r for r in rows if item['slug'] in {s['slug'] for s in r['stages']}]
        sections.append({**item,'issues':entries if stage else entries[:8],'count':len(entries)})
    context.update({'sections':sections,'stage':stage,'stage_choices':stage_choices,'query':query,'kind':kind,
                    'issue_count':sum(s['count'] for s in sections) if stage else len(rows),'total_issues':len(all_issues),'references':pests.sources()[1][crop['name']]['sources']})
    return render(request,'crops/pests.html',context)


def detail(request,crop_slug,issue_slug):
    context=selection(request,crop_slug)
    issue=next((r for r in pests.issues_for(context['crop']) if r['id']==issue_slug),None)
    if issue is None:raise Http404('This issue is not listed for this crop')
    context['issue']=issue
    return render(request,'crops/pest_detail.html',context)
