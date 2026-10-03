"""Viv's Operations Report Builder. Run: python -m streamlit run app.py"""
from datetime import date
from pathlib import Path
import hashlib
import html
import io
import json
import zipfile
import pandas as pd
import streamlit as st
from core import PERIODS, DATE_FORMATS, period_bounds, load_file, sample_data, build_report
from exports import excel_bytes, pdf_bytes, display_records
from design import CSS, hero_html

FIELDS = ['Activity date', 'Status', 'Activity', 'Owner', 'Due date', 'Completed date', 'Category', 'Value']
ALIASES = {
 'Activity date':['activity date','date','created date','created at','booking date'],
 'Status':['status','task status','booking status'], 'Activity':['activity','task','task name','description','title'],
 'Owner':['owner','assigned to','assignee','team member'], 'Due date':['due date','deadline'],
 'Completed date':['completed date','completion date','completed at'], 'Category':['category','department','type'],
 'Value':['value','amount','total','revenue']}

def guess(field, columns):
    clean=lambda v:str(v).strip().lower().replace('_',' ')
    return next((c for c in columns if clean(c) in ALIASES[field]),None)

@st.dialog('Terms and Policies', width='large')
def policies():
    texts={
    'Privacy Policy':'Files are processed to prepare the report you request. This app does not intentionally save uploaded files to disk, send them to an AI service, or share them with other users. Data and generated reports remain in server memory during your session. Hosting providers may process technical logs and metadata. Closing a tab does not guarantee immediate memory deletion. Avoid highly sensitive or confidential uploads on a public deployment.',
    'Terms & Conditions':'Use only data you are authorized to process. This is a portfolio productivity tool. You are responsible for the column mapping, date format, status rules, and checking the final report. Outputs are provided without a guarantee of accuracy or suitability for every business system. Do not use the app for unlawful purposes.',
    'Cookie Policy':'The app does not intentionally add advertising or marketing cookies. Streamlit and the hosting platform may use necessary cookies or similar technologies. Review and update this policy and consent controls if additional services or analytics are introduced.',
    'Data Upload Consent':'Uploading and processing a file confirms that you have permission to use its data. The upload screen asks for your confirmation before processing. Use fictional sample data to explore the public demo.',
    'Accessibility':'The interface uses descriptive controls, readable contrast, keyboard focus indicators, and a responsive layout. Charts include data tables. Accessibility has not been formally certified; improvements can be made as the project develops.',
    'Refund Policy':'This portfolio version has no paid checkout or subscription, so no payment refunds apply. If paid services are introduced, publish the applicable terms before collecting payment.',
    'Important Notice':'One row is counted as one activity. The app does not infer unique tasks, remove duplicate records, or reconstruct historical status changes. Reports describe the selected dataset and counting rules. Review methodology and data issues before sharing or making decisions.'}
    for title,text in texts.items():
        with st.expander(title): st.write(text)

def footer():
    with st.container(key='policy_footer'):
        st.markdown('<p class="footer-copy">© 2026 FVA</p>',unsafe_allow_html=True)
        if st.button('Terms and Policies',key='policies_button',type='tertiary'): policies()

def landing():
    st.markdown(hero_html(),unsafe_allow_html=True)
    with st.container(key='hero_action'):
        left,center,right=st.columns([1,2.4,1])
        with center:
            if st.button('PROCESS YOUR DATA HERE',type='primary',width='stretch'):
                st.session_state['workspace']=True;st.rerun()
    st.markdown('<p class="intro-note">Welcome to Viv’s Operations Report Builder.<br>Turn your spreadsheets into weekly, monthly, quarterly, and annual reports. Upload your data, choose the period, review the results, and export.</p>',unsafe_allow_html=True)
    footer()

def workspace():
    st.markdown('<div class="brandbar"><strong>Viv’s Operations Report Builder</strong><span>DATA ANALYSIS / REPORT WORKSPACE</span></div>',unsafe_allow_html=True)
    if st.button('← Back to welcome',type='tertiary'):
        st.session_state['workspace']=False;st.rerun()
    st.markdown('<p class="step">01 / Your dataset</p>',unsafe_allow_html=True)
    source=st.radio('Choose a source',['Sample dataset','Upload your file'],horizontal=True)
    uploaded=None
    if source=='Sample dataset':
        original=sample_data(); digest='sample'; filename='sample_operations.csv'
        st.caption('Fictional portfolio data spanning 2025–2026. Every row represents one activity.')
        st.download_button('Download sample CSV',original.to_csv(index=False).encode('utf-8-sig'),'sample_operations.csv','text/csv')
    else:
        consent=st.checkbox('I am authorized to process this data and have read the upload and privacy policies.')
        uploaded=st.file_uploader('Upload CSV, TSV, or Excel',type=['csv','tsv','xlsx'],disabled=not consent)
        st.caption('Use a table with one activity per row, a header row, an activity date, and a status. Excel dates stored as dates are supported. Public demos are best explored with fictional data.')
        if not consent or uploaded is None:
            footer();return
        raw=uploaded.getvalue();filename=uploaded.name
        if len(raw)>20*1024*1024:
            st.error('Please use a file of 20 MB or less.');footer();return
        encoding,separator,sheet='utf-8-sig','Auto-detect',0
        try:
            with st.expander('Import settings'):
                if filename.lower().endswith('.xlsx'):
                    sheets=pd.ExcelFile(io.BytesIO(raw),engine='openpyxl').sheet_names
                    sheet=st.selectbox('Worksheet',sheets)
                    st.caption('One worksheet is reported at a time. Formatting and macros are not imported.')
                else:
                    enc=st.selectbox('File encoding',['UTF-8','Windows-1252','UTF-16'])
                    encoding={'UTF-8':'utf-8-sig','Windows-1252':'cp1252','UTF-16':'utf-16'}[enc]
                    separator=st.selectbox('Column separator',['Auto-detect','Comma','Tab','Semicolon','Pipe'])
            original=load_file(raw,filename,encoding,separator,sheet)
            digest=hashlib.sha256(raw+str((encoding,separator,sheet)).encode()).hexdigest()[:12]
        except (UnicodeError,ValueError,pd.errors.ParserError,pd.errors.EmptyDataError,zipfile.BadZipFile,KeyError,OSError) as e:
            st.error('The file could not be read. Check its format, encoding, column separator, or worksheet.');footer();return
    if original.empty:
        st.info('This table has no activity rows. Try the sample or upload a populated table.');footer();return
    original.columns=[str(c) for c in original.columns]
    if original.columns.duplicated().any():
        st.error('Column names must be unique. Rename repeated headers and upload again.');footer();return
    st.caption(f'{filename} · {len(original):,} rows · {len(original.columns)} columns')
    with st.expander('Preview source data'):
        st.dataframe(original.head(50),width='stretch',hide_index=True)
        st.caption('Preview shows the first 50 rows; the report uses the complete dataset.')
    st.markdown('<p class="step">02 / Match your columns</p>',unsafe_allow_html=True)
    st.caption('Activity date and Status are required. Optional columns add workload, overdue, category, and value analysis.')
    mapping={}; columns=list(original.columns)
    pairs=st.columns(2)
    for i,field in enumerate(FIELDS):
        options=['Not mapped']+columns
        found=guess(field,columns)
        with pairs[i%2]:
            chosen=st.selectbox(field+(' *' if field in FIELDS[:2] else ''),options,index=options.index(found) if found else 0,key=f'map_{digest}_{field}')
            mapping[field]=None if chosen=='Not mapped' else chosen
    if not all(mapping[f] for f in FIELDS[:2]):
        st.info('Select an activity-date column and a status column to continue.');footer();return
    selected=[c for c in mapping.values() if c]
    if len(selected)!=len(set(selected)):
        st.error('Map each source column to only one field.');footer();return
    st.markdown('<p class="step">03 / Choose your report</p>',unsafe_allow_html=True)
    a,b,c=st.columns([1,1,1.2])
    with a: kind=st.selectbox('Reporting frequency',PERIODS)
    with b: anchor=st.date_input('A date within the period',value=date(2026,9,15) if source=='Sample dataset' else pd.Timestamp.now(tz='Asia/Manila').date())
    with c: fmt=st.selectbox('Text date format',list(DATE_FORMATS))
    start,end=period_bounds(kind,anchor)
    st.caption(f'Selected period: {start:%d %b %Y} – {end:%d %b %Y}. Weeks run Monday–Sunday; quarters and years follow the calendar.')
    status_values=sorted(set(original[mapping['Status']].astype('string').fillna('').str.strip().replace('','Unknown').tolist()))
    def default_status(names): return [v for v in status_values if v.lower() in names]
    a,b=st.columns(2)
    with a: done=st.multiselect('Statuses counted as completed',status_values,default=default_status(['completed','complete','done','closed','resolved']),key=f'done_{digest}_{mapping["Status"]}')
    with b: excluded=st.multiselect('Statuses excluded from completion rate',status_values,default=default_status(['cancelled','canceled']),key=f'excluded_{digest}_{mapping["Status"]}')
    if set(done)&set(excluded):
        st.error('A status cannot be both completed and excluded.');footer();return
    if not done: st.caption('No completed statuses selected: completed count will be zero.')
    title=st.text_input('Report title',value='Operations Performance Report',max_chars=100)
    value_label=st.text_input('Numeric total label',value='Activity value',max_chars=50) if mapping['Value'] else 'Activity value'
    value_label=value_label.strip() or 'Activity value'
    if value_label in ['Activities','Completed','Open','Overdue','Excluded statuses','Completion rate (%)','Previous period activities','Activity change']:
        st.error('Choose a distinct label for the numeric total.');footer();return
    signature=hashlib.sha256(json.dumps([digest,mapping,kind,str(anchor),fmt,done,excluded,title,value_label],sort_keys=True).encode()).hexdigest()
    if st.button('GENERATE OPERATIONS REPORT',type='primary',width='stretch'):
        with st.spinner('Building your report…'):
            r=build_report(original,mapping,kind,anchor,fmt,done,excluded,title.strip() or 'Operations Performance Report',value_label.strip() or 'Activity value')
            st.session_state['report']=r;st.session_state['report_signature']=signature
            st.session_state.pop('export_bytes',None)
    if 'report' not in st.session_state:
        footer();return
    if signature!=st.session_state.get('report_signature'):
        st.info('Settings changed. Generate the report again to apply them.');footer();return
    r=st.session_state['report']
    st.divider()
    st.markdown(f'<h2 class="report-title">{html.escape(r["title"])}</h2><p class="report-meta">{r["kind"].upper()} / {r["start"]} — {r["end"]} / CUTOFF {r["as_of"]}</p>',unsafe_allow_html=True)
    st.markdown('<div class="kpis">'+''.join(f'<div class="kpi"><b>{r["metrics"][k]:,}</b><span>{k}</span></div>' for k in ['Activities','Completed','Open','Overdue'])+'</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="summary">{html.escape(r["summary"])}</div>',unsafe_allow_html=True)
    if r['records'].empty: st.info('No activities fall in this period. Select another period or check the date mapping. Empty exports remain available.')
    completion,comparison=st.columns(2)
    with completion: st.metric('Completion rate',f'{r["metrics"]["Completion rate (%)"]:.1f}%')
    with comparison: st.metric('Previous period activities',r['metrics']['Previous period activities'],delta=f'{r["metrics"]["Activity change"]:+d} activity count change',delta_color='off')
    tabs=st.tabs(['Overview','Team workload','Activities','Data quality & rules','Export report'])
    with tabs[0]:
        a,b=st.columns(2)
        with a:
            st.subheader('Status breakdown')
            if not r['statuses'].empty: st.bar_chart(r['statuses'],x='Status',y='Activities',color='#00813a')
            st.dataframe(r['statuses'],width='stretch',hide_index=True)
        with b:
            st.subheader('Activity trend')
            if not r['trend'].empty: st.bar_chart(r['trend'],x='Period',y='Activities',color='#e3a13c')
            st.dataframe(r['trend'],width='stretch',hide_index=True)
        if mapping['Value']:
            v=r['metrics'].get(value_label.strip() or 'Activity value')
            st.metric(value_label.strip() or 'Activity value','Not available' if v is None else f'{v:,.2f}')
            st.caption('Sum of valid numeric values for all period activities, including excluded statuses. This is not automatically a revenue figure.')
        if mapping['Category']:
            st.subheader('By category');st.dataframe(r['records'].groupby('Category').size().reset_index(name='Activities'),hide_index=True,width='stretch')
    with tabs[1]:
        st.dataframe(r['owners'],hide_index=True,width='stretch')
        if not mapping['Owner']: st.caption('Map an owner column to separate team workloads.')
    with tabs[2]:
        only_overdue=st.checkbox('Show only overdue activities')
        records=r['records'].loc[r['records']['Overdue by cutoff']] if only_overdue else r['records']
        st.dataframe(display_records(records.head(500)),hide_index=True,width='stretch')
        st.caption(f'{min(len(records),500):,} of {len(records):,} activities shown. Excel includes the complete selected-period dataset.')
    with tabs[3]:
        for note in r['notes']: st.write('• '+note)
        if not r['issues'].empty: st.dataframe(r['issues'],hide_index=True,width='stretch')
        st.caption('No duplicate removal or automatic date-format guessing. Fix source records or change the mapping before regenerating.')
    with tabs[4]:
        st.write('Review the summary, activity list, and counting rules before sharing.')
        if 'export_bytes' not in st.session_state:
            st.session_state['export_bytes']=(excel_bytes(r),pdf_bytes(r))
        xlsx,pdf=st.session_state['export_bytes']
        stem=f'operations_{kind.lower()}_{start.isoformat()}'
        a,b=st.columns(2)
        with a: st.download_button('DOWNLOAD EXCEL REPORT',xlsx,stem+'.xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',type='primary',width='stretch')
        with b: st.download_button('DOWNLOAD PDF REPORT',pdf,stem+'.pdf','application/pdf',type='primary',width='stretch')
        st.caption('Excel includes summary, all activities, workload, status, trend, data issues, methodology, and settings. PDF includes the summary and up to 30 overdue activities.')
    footer()

def main():
    st.set_page_config(page_title='Viv’s Operations Report Builder',page_icon=str(Path(__file__).parent/'favicon.png'),layout='wide')
    st.markdown(CSS,unsafe_allow_html=True)
    st.session_state.setdefault('workspace',False)
    if st.session_state['workspace']: workspace()
    else: landing()

if __name__=='__main__': main()
