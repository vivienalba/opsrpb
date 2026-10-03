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
from design import CSS, hero_html, masthead_html, steps_html

FIELDS = ['Activity date', 'Status', 'Activity', 'Owner', 'Due date', 'Completed date', 'Category', 'Value']
ALIASES = {
    'Activity date':['activity date','date','created date','created at','booking date'],
    'Status':['status','task status','booking status'],
    'Activity':['activity','task','task name','description','title'],
    'Owner':['owner','assigned to','assignee','team member'],
    'Due date':['due date','deadline'], 'Completed date':['completed date','completion date','completed at'],
    'Category':['category','department','type'], 'Value':['value','amount','total','revenue'],
}


def guess(field, columns):
    def normalized(value): return str(value).strip().lower().replace('_',' ')
    return next((column for column in columns if normalized(column) in ALIASES[field]), None)


@st.dialog('Terms and Policies', width='large')
def policies():
    texts = {
        'Privacy Policy':'Files are processed to prepare the report you request. This app does not intentionally save uploaded files to disk, send them to an AI service, or share them with other users. Data and generated reports remain in server memory during your session. Hosting providers may process technical logs and metadata. Closing a tab does not guarantee immediate memory deletion. Avoid highly sensitive or confidential uploads on a public deployment.',
        'Terms & Conditions':'Use only data you are authorized to process. This is a portfolio productivity tool. You are responsible for the column mapping, date format, status rules, and checking the final report. Outputs are provided without a guarantee of accuracy or suitability for every business system. Do not use the app for unlawful purposes.',
        'Cookie Policy':'The app does not intentionally add advertising or marketing cookies. Streamlit and the hosting platform may use necessary cookies or similar technologies. Review and update this policy and consent controls if additional services or analytics are introduced.',
        'Data Upload Consent':'Uploading and processing a file confirms that you have permission to use its data. The upload screen asks for your confirmation before processing. Use fictional sample data to explore the public demo.',
        'Accessibility':'The interface uses descriptive controls, readable contrast, keyboard focus indicators, and a responsive layout. Charts include data tables. Accessibility has not been formally certified; improvements can be made as the project develops.',
        'Refund Policy':'This portfolio version has no paid checkout or subscription, so no payment refunds apply. If paid services are introduced, publish the applicable terms before collecting payment.',
        'Important Notice':'One row is counted as one activity. The app does not infer unique tasks, remove duplicate records, or reconstruct historical status changes. Reports describe the selected dataset and counting rules. Review methodology and data issues before sharing or making decisions.',
    }
    for title, text in texts.items():
        with st.expander(title): st.write(text)


def footer():
    with st.container(key='policy_footer'):
        st.markdown('<p class="footer-copy">© 2026 FVA</p>',unsafe_allow_html=True)
        if st.button('Terms and Policies',key='policies_button',type='tertiary'): policies()


def open_workspace(source):
    st.session_state['workspace'] = True
    st.session_state['data_source'] = source


def landing():
    st.markdown(masthead_html()+hero_html(),unsafe_allow_html=True)
    with st.container(key='hero_action'):
        action, support = st.columns([1,1.15],gap='large',vertical_alignment='center')
        with action:
            start, sample = st.columns([1.1,1])
            with start:
                st.button('Start a report →',key='start_report',type='primary',width='stretch',on_click=open_workspace,args=('Upload your file',))
            with sample:
                st.button('Try sample data',key='sample_demo',width='stretch',on_click=open_workspace,args=('Sample dataset',))
        with support:
            st.markdown('<p class="welcome-help">Bring your records. Choose a period. Review your results.<br>Take a report you can share into your next meeting.</p>',unsafe_allow_html=True)
    st.markdown(steps_html(),unsafe_allow_html=True)
    footer()


def section_heading(number, title):
    st.markdown(f'<div class="setup-heading"><b>{number}</b><h2>{title}</h2></div>',unsafe_allow_html=True)


def get_source():
    with st.container(key='dataset_card'):
        section_heading('01','Bring your records')
        source = st.radio('Choose a source',['Sample dataset','Upload your file'],horizontal=True,key='data_source',label_visibility='collapsed')
        if source == 'Sample dataset':
            original = sample_data()
            digest, filename = 'sample', 'sample_operations.csv'
            st.caption('Fictional operations records from 2025–2026. One row represents one activity.')
            st.download_button('Get the sample CSV',original.to_csv(index=False).encode('utf-8-sig'),'sample_operations.csv','text/csv')
        else:
            consent = st.checkbox('I have permission to process this data and have read the upload and privacy policies.',key='upload_consent')
            uploaded = st.file_uploader('Upload CSV, TSV, or Excel',type=['csv','tsv','xlsx'],disabled=not consent)
            st.caption('Use a header row and one activity per row. You’ll match the activity date and status next.')
            if not consent or uploaded is None: return None
            raw, filename = uploaded.getvalue(), uploaded.name
            if len(raw) > 20*1024*1024:
                st.error('Please use a file of 20 MB or less.'); return None
            encoding, separator, sheet = 'utf-8-sig','Auto-detect',0
            try:
                with st.expander('Import settings'):
                    if filename.lower().endswith('.xlsx'):
                        sheets = pd.ExcelFile(io.BytesIO(raw),engine='openpyxl').sheet_names
                        sheet = st.selectbox('Worksheet',sheets)
                        st.caption('Choose one worksheet for this report. The source workbook is unchanged.')
                    else:
                        enc = st.selectbox('File encoding',['UTF-8','Windows-1252','UTF-16'])
                        encoding = {'UTF-8':'utf-8-sig','Windows-1252':'cp1252','UTF-16':'utf-16'}[enc]
                        separator = st.selectbox('Column separator',['Auto-detect','Comma','Tab','Semicolon','Pipe'])
                original = load_file(raw,filename,encoding,separator,sheet)
                digest = hashlib.sha256(raw+str((encoding,separator,sheet)).encode()).hexdigest()[:12]
            except (UnicodeError,ValueError,pd.errors.ParserError,pd.errors.EmptyDataError,zipfile.BadZipFile,KeyError,OSError):
                st.error('The file could not be read. Check its format, encoding, separator, or worksheet.'); return None
        if original.empty:
            st.info('This table has no activity rows. Try the sample or upload a populated table.'); return None
        original.columns = [str(c) for c in original.columns]
        if original.columns.duplicated().any():
            st.error('Column names must be unique. Rename repeated headers and upload again.'); return None
        st.caption(f'{filename} · {len(original):,} rows · {len(original.columns)} columns')
        with st.expander('Preview your records'):
            st.dataframe(original.head(50),width='stretch',hide_index=True)
            st.caption('First 50 rows shown. Your report uses the complete dataset.')
        return original, digest, filename, source


def get_settings(original, digest, source):
    mapping = {}
    columns = list(original.columns)
    def mapping_control(field):
        options = ['Not mapped']+columns
        found = guess(field,columns)
        chosen = st.selectbox(field+(' *' if field in FIELDS[:2] else ''),options,index=options.index(found) if found else 0,key=f'map_{digest}_{field}')
        mapping[field] = None if chosen == 'Not mapped' else chosen
    left, right = st.columns([1,1],gap='large')
    with left, st.container(key='mapping_card'):
        section_heading('02','Match your columns')
        st.caption('Two required fields, then as much detail as you need.')
        for field in FIELDS[:2]: mapping_control(field)
        with st.expander('Optional fields · add more detail'):
            st.caption('Owners add team workload. Due dates add overdue counts. Completion dates verify timing.')
            for field in FIELDS[2:]: mapping_control(field)
        fmt = st.selectbox('Text date format',list(DATE_FORMATS),help='Choose the format used in your source text dates. Excel cells stored as dates are recognized directly.')
        st.caption('We suggest matching columns by their names. Check each selection before building your report.')
    with right, st.container(key='period_card'):
        section_heading('03','Choose your perspective')
        kind = st.selectbox('Reporting frequency',PERIODS)
        anchor = st.date_input('A date within the period',value=date(2026,9,15) if source == 'Sample dataset' else pd.Timestamp.now(tz='Asia/Manila').date())
        start, end = period_bounds(kind,anchor)
        st.caption(f'{start:%d %b %Y} – {end:%d %b %Y}. Weeks start Monday. Quarters and years follow the calendar.')
        statuses = sorted(set(original[mapping['Status']].astype('string').fillna('').str.strip().replace('','Unknown').tolist())) if mapping['Status'] else []
        def defaults(names): return [v for v in statuses if v.lower() in names]
        done = st.multiselect('Statuses counted as completed',statuses,default=defaults(['completed','complete','done','closed','resolved']),key=f'done_{digest}_{mapping["Status"]}')
        excluded = st.multiselect('Statuses excluded from completion rate',statuses,default=defaults(['cancelled','canceled']),key=f'excluded_{digest}_{mapping["Status"]}')
        with st.expander('Report details'):
            title = st.text_input('Report title',value='Operations Performance Report',max_chars=100)
            value_label = st.text_input('Numeric total label',value='Activity value',max_chars=50) if mapping['Value'] else 'Activity value'
        st.caption('The activity date determines which rows belong in the period. Review counting rules with your results.')
    if not all(mapping[f] for f in FIELDS[:2]):
        st.info('Select an activity-date column and a status column to continue.'); return None
    selected = [c for c in mapping.values() if c]
    if len(selected) != len(set(selected)):
        st.error('Match each source column to only one field.'); return None
    if set(done) & set(excluded):
        st.error('A status cannot be both completed and excluded.'); return None
    if not done: st.caption('No completed statuses selected. The completed count will be zero.')
    value_label = value_label.strip() or 'Activity value'
    if value_label in ['Activities','Completed','Open','Overdue','Excluded statuses','Completion rate (%)','Previous period activities','Activity change']:
        st.error('Choose a distinct label for the numeric total.'); return None
    return mapping, kind, anchor, fmt, done, excluded, title.strip() or 'Operations Performance Report', value_label


def render_report(r, value_label):
    mapping, kind, start = r['mapping'], r['kind'], r['start']
    with st.container(key='report_card'):
        st.markdown(f'<div id="report-results" class="report-heading"><div><span class="report-label">Your report / ready to review</span><h2>{html.escape(r["title"])}</h2><p>{r["start"]:%d %b %Y} – {r["end"]:%d %b %Y} · Cutoff {r["as_of"]:%d %b %Y}</p></div><span class="frequency-tag">{kind}</span></div>',unsafe_allow_html=True)
        st.markdown('<div class="kpis">'+''.join(f'<div class="kpi"><b>{r["metrics"][k]:,}</b><span>{k}</span></div>' for k in ['Activities','Completed','Open','Overdue'])+'</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="summary"><div class="eyebrow">The period, at a glance</div>{html.escape(r["summary"])}</div>',unsafe_allow_html=True)
        if r['records'].empty: st.info('No activities fall in this period. Choose another period or check the date mapping. Empty exports remain available.')
        completion, comparison = st.columns(2)
        with completion: st.metric('Completion rate',f'{r["metrics"]["Completion rate (%)"]:.1f}%')
        with comparison: st.metric('Previous period activities',r['metrics']['Previous period activities'],delta=f'{r["metrics"]["Activity change"]:+d} activity count change',delta_color='off')
        tabs = st.tabs(['Overview','Team workload','Activities','Data quality & rules','Export report'])
        with tabs[0]:
            a,b = st.columns(2)
            with a, st.container(key='chart_status'):
                st.subheader('How the work stands')
                if not r['statuses'].empty: st.bar_chart(r['statuses'],x='Status',y='Activities',color='#60969f')
                with st.expander('View status data'): st.dataframe(r['statuses'],width='stretch',hide_index=True)
            with b, st.container(key='chart_trend'):
                st.subheader('Activity through the period')
                if not r['trend'].empty: st.bar_chart(r['trend'],x='Period',y='Activities',color='#d49762')
                with st.expander('View trend data'): st.dataframe(r['trend'],width='stretch',hide_index=True)
            if mapping['Value']:
                label = value_label
                value = r['metrics'].get(label)
                st.metric(label,'Not available' if value is None else f'{value:,.2f}')
                st.caption('Sum of valid numeric values for all period activities, including excluded statuses. This is not automatically a revenue figure.')
            if mapping['Category']:
                st.subheader('By category')
                st.dataframe(r['records'].groupby('Category').size().reset_index(name='Activities'),hide_index=True,width='stretch')
        with tabs[1]:
            st.subheader('A view across your team')
            st.dataframe(r['owners'],hide_index=True,width='stretch')
            if not mapping['Owner']: st.caption('Match an owner column to separate team workloads.')
        with tabs[2]:
            search, filter_column = st.columns([2,1],vertical_alignment='bottom')
            with search: query = st.text_input('Search activities',placeholder='Find an activity, owner, or status…',key='activity_search')
            with filter_column: only_overdue = st.checkbox('Only overdue activities')
            records = r['records'].loc[r['records']['Overdue by cutoff']] if only_overdue else r['records']
            records = display_records(records)
            if query.strip():
                mask = records.astype('string').apply(lambda c:c.str.contains(query.strip(),case=False,regex=False,na=False)).any(axis=1)
                records = records.loc[mask]
            st.dataframe(records.head(500),hide_index=True,width='stretch')
            st.caption(f'{min(len(records),500):,} of {len(records):,} matching activities shown. Excel includes all selected-period activities, regardless of this view.')
        with tabs[3]:
            st.subheader('The rules behind the numbers')
            for note in r['notes']: st.write('• '+note)
            if not r['issues'].empty:
                st.subheader('Records to review')
                st.dataframe(r['issues'],hide_index=True,width='stretch')
            st.caption('No duplicate removal or automatic date-format guessing. Fix source records or change the mapping before regenerating.')
        with tabs[4]:
            st.subheader('Take your report with you')
            st.caption('Review your activity list, data issues, and counting rules before sharing.')
            if 'export_bytes' not in st.session_state:
                st.session_state['export_bytes'] = (excel_bytes(r),pdf_bytes(r))
            xlsx,pdf = st.session_state['export_bytes']
            stem = f'operations_{kind.lower()}_{start.isoformat()}'
            a,b = st.columns(2)
            with a, st.container(key='export_excel'):
                st.subheader('The working report')
                st.markdown('<p class="export-note">Excel workbook · Complete activities, summary, workload, status, trend, data issues, methodology, and settings.</p>',unsafe_allow_html=True)
                st.download_button('Download Excel report',xlsx,stem+'.xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',type='primary',width='stretch',icon=':material/table_view:')
            with b, st.container(key='export_pdf'):
                st.subheader('The meeting copy')
                st.markdown('<p class="export-note">PDF report · Summary, metrics, workload, status, counting rules, and up to 30 overdue activities.</p>',unsafe_allow_html=True)
                st.download_button('Download PDF report',pdf,stem+'.pdf','application/pdf',type='primary',width='stretch',icon=':material/download:')


def workspace():
    st.markdown(masthead_html(workspace=True),unsafe_allow_html=True)
    if st.button('← Back to welcome',type='tertiary'):
        st.session_state['workspace'] = False
        st.rerun()
    st.markdown('<div class="workspace-heading"><p class="eyebrow">Your reporting desk</p><h1>Let’s put it in perspective.</h1><p>Bring your records, choose a period, and build a report to review.</p></div>',unsafe_allow_html=True)
    source = get_source()
    if source is None:
        footer(); return
    original, digest, filename, source_type = source
    settings = get_settings(original,digest,source_type)
    if settings is None:
        footer(); return
    mapping, kind, anchor, fmt, done, excluded, title, value_label = settings
    start,end = period_bounds(kind,anchor)
    signature = hashlib.sha256(json.dumps([digest,mapping,kind,str(anchor),fmt,done,excluded,title,value_label],sort_keys=True).encode()).hexdigest()
    with st.container(key='build_action'):
        st.markdown(f'<div class="brief"><div><b>{html.escape(title)}</b><p>{html.escape(filename)}</p></div><div><b>{start:%d %b} – {end:%d %b %Y}</b><p>{len(original):,} source rows to evaluate</p></div><div><span class="brief-tag">{kind} report</span></div></div>',unsafe_allow_html=True)
        if st.button('Generate operations report →',key='generate_report',type='primary',width='stretch'):
            with st.spinner('Putting your report together…'):
                r = build_report(original,mapping,kind,anchor,fmt,done,excluded,title,value_label)
                st.session_state['report'] = r
                st.session_state['report_signature'] = signature
                st.session_state.pop('export_bytes',None)
    if 'report' not in st.session_state:
        st.markdown('<div class="empty-report"><h3>Your next report starts here.</h3><p>Check your selections above, then generate a report.<br>Your summary, workload, and downloads will appear here.</p></div>',unsafe_allow_html=True)
    elif signature != st.session_state.get('report_signature'):
        st.info('Your selections changed. Generate the report again to update the results and downloads.')
    else:
        render_report(st.session_state['report'], value_label)
    footer()


def main():
    st.set_page_config(page_title='Viv’s Operations Report Builder',page_icon=str(Path(__file__).parent/'favicon.png'),layout='wide')
    st.markdown(CSS,unsafe_allow_html=True)
    st.session_state.setdefault('workspace',False)
    if st.session_state['workspace']: workspace()
    else: landing()


if __name__ == '__main__': main()
