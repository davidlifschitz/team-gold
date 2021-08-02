def run_import(number_of_quarters):
    # IMPORTS FOR CHECKING IF DB IS UP TO DATE
    import datetime as dt 
    #
    # IMPORTS FOR EDGAR
    from sec_api import QueryApi
    # IMPORTS FOR SQL DB CONNECTION
    import pymysql

    # CHANGE FIELDS TO YOUR OWN PERSONAL FIELDS
    db = pymysql.connect(
      host = 'your database hosting site',
      user = 'your username',
      password = 'your password',
      db = 'Name of the database you are connecting to'
    )
    c = db.cursor()

    #OUR WORKING DB
    # db = pymysql.connect(
    #     host='hedge-fund-13f-filings.cuqh3juyttmr.us-east-1.rds.amazonaws.com',
    #     user='admin',
    #     password='12345678',
    #     db='HF_13f_filings')
    # c = db.cursor()

    queryApi = QueryApi(api_key="Your API Key that can be obtained from the sec-api site") 
    
    cik = [
        "1423053",
        "1736225",
        "1294571",
        "1603466",
        "1569049",
        "1439289",
        "1401388",
        "1410830",
        "1389507",
        "1343781",
        "1350694",
        "1317679",
        "1318757",
        "1061165",
        "1092838",
        "1280493",
        "1273087",
        "1218710",
        "1166309",
        "1167483",
        "1136704",
        "1135730",
        "1106500",
        "1040198",
        "1040273",
        "1103804",
        "1029160",
        "934639",
        "1009207"
    ]

    all_filings = []

    for a in range(len(cik)):
        fund_cik = cik[a]
        query = {
            "query": {
                "query_string": {
                    "query": "cik %s AND formType:13F-HR" % fund_cik
                }
            },
            "from": "0",
            "size": "%s",
            "sort": [{"filedAt": {"order": "desc"}}]
        } % number_of_quarters
        print(query.get('query').get('query_string').get('query') + "fund_cik is: " + fund_cik)

        filings = queryApi.get_filings(query)
        #These next couple lines are to prevent double filings with a different fund which was occuring amongst a few of the funds
        set_size = 0
        for i in filings.get('filings'):
            if(set_size > 4):
                break
            set_size += 1
            if(i.get('cik') != fund_cik):
                continue
            if(i.get('holdings') == None):
                continue
            if(i.get('periodOfReport') == None):
                continue
            filingDate = i.get('periodOfReport')        
            cik_of_fund = i.get('cik')
            fund_name = i.get('companyNameLong')
            for j in i.get('holdings'):
                all_filings.append(j)
                s = j.get('shrsOrPrnAmt')
                shares = str(s.get('sshPrnamt'))        
                value = str(j.get('value'))                    
                cusip = str(j.get('cusip'))        
                nameOfIssuer = str(j.get('nameOfIssuer'))
                sql = "INSERT INTO FakeTableWithAllHoldings (cusip, nameOfIssuer, shares, value, filingDate, CIK) VALUES (%s, %s, %s, %s, %s, %s)" 
                c.execute(sql,(cusip, nameOfIssuer, shares, value, filingDate,cik[a]))
                db.commit()     
        print("finished with fund: " + fund_name)