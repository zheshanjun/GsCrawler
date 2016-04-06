# coding=gbk

from TableTemplate import TableTemplate


jiben_template = TableTemplate('Registered_Info', u'������Ϣ')
jiben_template.column_dict = {
    u'ͳһ������ô���/ע���': 'RegistrationNo',
    u'ע���/ͳһ������ô���': 'RegistrationNo',             # Modified by Jing
    u'ע���': 'RegistrationNo',                        # Modified by Jing
    u'����': 'EnterpriseName',
    u'ʡ��': 'Province',
    u'����������': 'LegalRepresentative',
    u'��Ӫ��': 'Operator',                              # Modified by Jing
    u'����': 'EnterpriseType',
    u'�����ʽ': 'CompositionForm',                       # Modified by Jing
    u'��������': 'EstablishmentDate',
    u'ע������': 'EstablishmentDate',                    # Modified by Jing
    u'ע���ʱ�': 'RegisteredCapital',
    u'ס��': 'ResidenceAddress',
    u'Ӫҵ������': 'ValidityFrom',
    u'Ӫҵ������': 'ValidityTo',
    u'��Ӫ������': 'ValidityFrom',
    u'��Ӫ������': 'ValidityTo',
    u'��Ӫ��Χ': 'BusinessScope',
    u'�Ǽǻ���': 'RegistrationInstitution',
    u'��׼����': 'ApprovalDate',
    u'�Ǽ�״̬': 'RegistrationStatus',
    u'������': 'principal',
    u'Ӫҵ����': 'businessPlace',
    u'��Ӫ����': 'businessPlace',                        # Modified by Jing
    u'��������': 'RevocationDate',
    u'Ͷ����': 'investor',
    u'ִ������ϻ���': 'ExecutivePartner',
    u'��Ҫ��Ӫ����': 'MianBusinessPlace',
    u'�ϻ�������': 'PartnershipFrom',
    u'�ϻ�������': 'PartnershipTo'
}

gudong_template = TableTemplate('Shareholder_Info', u'�ɶ���Ϣ')
gudong_template.column_list = ['Shareholder_Name', 'Shareholder_CertificationType', 'Shareholder_CertificationNo', 'Shareholder_Type', 'Shareholder_Details',
                               'Subscripted_Capital', 'ActualPaid_Capital', 'Subscripted_Method', 'Subscripted_Amount', 'Subscripted_Time', 'ActualPaid_Method',
                               'ActualPaid_Amount', 'ActualPaid_Time']

biangeng_template = TableTemplate('Changed_Announcement', u'�����Ϣ')
biangeng_template.column_list = ['ChangedAnnouncement_Events', 'ChangedAnnouncement_Before', 'ChangedAnnouncement_After', 'ChangedAnnouncement_Date']

zhuyaorenyuan_template = TableTemplate('KeyPerson_Info', u'��Ҫ��Ա��Ϣ')
zhuyaorenyuan_template.column_list = ['KeyPerson_No', 'KeyPerson_Name', 'KeyPerson_Position']

jiatingchengyuan_template = TableTemplate('Family_Info', u'�μӾ�Ӫ�ļ�ͥ��Ա����')    # Modified by Jing
jiatingchengyuan_template.column_list = ['FamilyMember_No', 'FamilyMember_Name', 'FamilyMember_Position']

fenzhijigou_template = TableTemplate('Branches', u'��֧������Ϣ')
fenzhijigou_template.column_list = ['Branch_No', 'Branch_RegistrationNo', 'Branch_RegistrationName', 'Branch_RegistrationInstitution']

qingsuan_template = TableTemplate('liquidation_Information', u'������Ϣ')
qingsuan_template.column_list = ['liquidation_PIC', 'liquidation_Member']

dongchandiyadengji_template = TableTemplate('Chattel_Mortgage', u'������Ѻ�Ǽ���Ϣ')
dongchandiyadengji_template.column_list = ['ChattelMortgage_No', 'ChattelMortgage_RegistrationNo', 'ChattelMortgage_RegistrationDate',
                                           'ChattelMortgage_RegistrationInstitution', 'ChattelMortgage_GuaranteedAmount', 'ChattelMortgage_Status',
                                           'ChattelMortgage_AnnounceDate', 'ChattelMortgage_Details']

guquanchuzhidengji_template = TableTemplate('Equity_Pledge', u'��Ȩ���ʵǼ���Ϣ')
guquanchuzhidengji_template.column_list = ['EquityPledge_No', 'EquityPledge_RegistrationNo', 'EquityPledge_Pledgor', 'EquityPledge_PledgorID',
                                           'EquityPledge_Amount', 'EquityPledge_Pawnee', 'EquityPledge_PawneeID', 'EquityPledge_RegistrationDate',
                                           'EquityPledge_Status', 'EquityPledge_AnnounceDate', 'EquityPledge_Change']

xingzhengchufa_template = TableTemplate('Administrative_Penalty', u'����������Ϣ')
xingzhengchufa_template.column_list = ['Penalty_No', 'Penalty_Code', 'Penalty_IllegalType', 'Penalty_DecisionContent',
                                       'Penalty_DecisionInsititution', 'Penalty_DecisionDate', 'Penalty_Details']

jingyingyichang_template = TableTemplate('Business_Abnormal', u'��Ӫ�쳣��Ϣ')
jingyingyichang_template.column_list = ['Abnormal_No', 'Abnormal_Events', 'Abnormal_DatesIn', 'Abnormal_MoveoutReason',
                                        'Abnormal_DatesOut', 'Abnormal_DecisionInstitution']

yanzhongweifa_template = TableTemplate('Serious_Violations', u'����Υ����Ϣ')
yanzhongweifa_template.column_list = ['Serious_No', 'Serious_Events', 'Serious_DatesIn', 'Serious_MoveoutReason',
                                      'Serious_DatesOut', 'Serious_DecisionInstitution']

chouchajiancha_template = TableTemplate('Spot_Check', u'�������Ϣ')
chouchajiancha_template.column_list = ['Check_No', 'Check_Institution', 'Check_Type',
                                       'Check_Date', 'Check_Result', 'Check_Remark']


# def delete_from_db(code):
#     jiben_template.delete_from_database(code)
#     gudong_template.delete_from_database(code)
#     biangeng_template.delete_from_database(code)
#     zhuyaorenyuan_template.delete_from_database(code)
#     fenzhijigou_template.delete_from_database(code)
#     qingsuan_template.delete_from_database(code)
#     dongchandiyadengji_template.delete_from_database(code)
#     guquanchuzhidengji_template.delete_from_database(code)
#     xingzhengchufa_template.delete_from_database(code)
#     jingyingyichang_template.delete_from_database(code)
#     yanzhongweifa_template.delete_from_database(code)
#     chouchajiancha_template.delete_from_database(code)
