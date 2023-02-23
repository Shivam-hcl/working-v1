# %%
from __future__ import unicode_literals
from __future__ import print_function

# %%
import spacy
import neuralcoref
import re
import logging


# %%
logging.basicConfig( level=logging.INFO,filename='app.log', filemode='w', format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
# logging.warning('This will get logged to a file')

# %%
customWords = ['between','among','amongst']
stripCharacters=".!@#$%^&*()?_/\|<>,:; "

# %%
"""version 1.2
Config file for Comprehension Model"""
lang = 'en_core_web_sm'
greedyness = 0.55

unicode_ = str 

# %%
nlp=spacy.load(lang)
coref=neuralcoref.NeuralCoref(nlp.vocab,greedyness=greedyness)
nlp.add_pipe(coref,name="neuralcoref")

# %%
def corefResoultion(text1,text2):
	logging.info("control inside corefResoultion")

	try:
		text1 =text1.lower()
		text2 =text2.lower()
		text = text1+". "+text2
		doc = nlp(unicode_(text))
		corefStatus=doc._.has_coref
		
		if not corefStatus:
			text=text1+"  "+text2
			doc = nlp(unicode_(text))
			corefStatus = doc._.has_coref
			
		if not corefStatus:
			text=text1.title()+"    "+text2
			doc = nlp(unicode_(text))
			corefStatus = doc._.has_coref

	except Exception as err:
		print("Exception Occured",err)
		doc=""
		corefStatus=False
		raise
	return doc,corefStatus


# %%
def endCharCheck(orgText,modText):
    logging.info("control inside endCharCheck")
    try:
        if orgText[-1].isalnum():
            modText = modText
        else:
            modText = modText+orgText[-1]
    except Exception as err:
        print("Exception Occured",err)
        modText=""
        raise
    return modText
	

# %%
def resolveText(doc,text1,text2,customWord): # text2 -> query
    logging.info("control inside resolve test")
    try:
        rText="" 
        tempText1 = text1.rstrip(stripCharacters)
        tempText2 = text2.rstrip(stripCharacters)
       
        for cCount in range(len(doc._.coref_clusters)):
            mentionList=doc._.coref_clusters[cCount].mentions
           
            mCorefWord=doc._.coref_clusters[cCount].main.text.rstrip(stripCharacters)
            pronounList=[]
            mCount =0
            mCorefWord =mCorefWord.lstrip(stripCharacters)
            tokenMCorefWord=nlp(mCorefWord)
            for i in mentionList:
                x=nlp(str(i).lower())
                for token in x:
                    if token.pos_ == "PRON" :
                        pronounList.append(str(i))
                
            if mCorefWord.lower()!=tempText1.lower() and 	mCorefWord.lower() != tempText2.lower():
                corefWordList=[]
                corefWord =""
                for token in tokenMCorefWord:
                    if token.pos_ !="PRON" :
                        if token.text.upper() in text1:
                            corefWordList.append(token.text.upper())
                        elif token.text.title() in text1:
                            corefWordList.append(token.text.title())
                        elif token.text.lower() in text1:
                            corefWordList.append(token.text.lower())
                        else:
                             corefWordList.append(token.text)
                if len(corefWordList) >1 :
                    corefWord =' '.join(corefWordList)
                elif len(corefWordList) == 1:
                    corefWord = corefWordList[0]
                else:
                    corefWord =""

                text2 = text2.rstrip(stripCharacters)		
                docNoun = nlp(text2.lower())
                NounList= [ token.text for token in docNoun if token.pos_ == "NOUN" or token.pos_ == "PROPN" ]

                if len(pronounList) > 0 and corefWord !="":
                    for element in pronounList:
                        if not customWord:
                            if element not in NounList:
                                if element.upper() in text2:
                                    subWord=r'\b'+element.upper()+'\\b'
                                    text2=re.sub(subWord,corefWord,text2)
                                elif element in text2.lower():
                                    subWord=r'\b'+element+'\\b'
                                    text2=re.sub(subWord,corefWord,text2)
                                else:
                                    text2 =text2
                        else:
                            if element.upper() in text2:
                                subWord=r'\b'+element.upper()+'\\b'
                                text2=re.sub(subWord,corefWord,text2)
                            elif element in text2.lower():
                                    subWord=r'\b'+element+'\\b'
                                    text2=re.sub(subWord,corefWord,text2)
                            else:
                                    text2 =text2
            else:
                text2 = text2

        rText = text2
    except Exception as err:
        print("Exception Occured",err)
        rText=""
        raise
    
    return rText

# %%
def customWordResolve(stringList,textR,query):
    logging.info("control inside customWordResolve")
    try:
        tempText = textR
        customRText =""
        stringList = list(set(stringList))
        if len(stringList) > 1:
            corefWord = ','.join(stringList)
        elif len(stringList) != 0 :
            corefWord = stringList[0]
        else:
            corefWord =""	
        for ele in stringList:
            if ele.upper() in textR:
                subWord=r'\b'+str(ele).upper()+'\\b'
                textR=re.sub(subWord,corefWord,textR)
                break
            elif ele.title() in textR:
                subWord=r'\b'+str(ele).title()+'\\b'
                textR=re.sub(subWord,corefWord,textR)
                break
            elif len(ele)>1 and ele.lower() in textR:
                subWord=r'\b'+str(ele).lower()+'\\b'
                textR=re.sub(subWord,corefWord,textR)
                break
            else:
                textR =textR
        customRText = endCharCheck(query,textR)
    except Exception as err:
        print("Exception Occured",err)
        customRText=""
		
        raise	
    return customRText
            
            



# %%
def evalute_result(previous_statements,query):
    logging.info('Input values previous_statements'+str(previous_statements)+" Query: "+query)
    if len(previous_statements)==0 or previous_statements[0]=="":
        print("Two statements are required \n -Please provide atleast one input / first statement cant be blank") #this print statements can be replaced with return 
        logging.error("Two statements are required -Please provide atleast one input / first statement cant be blank")
        return
    if len(previous_statements)==1:
        logging.info("User provided only one value.Result will be on the basis of single value")
        data= previous_statements[0]
        previous_statements.insert(0, data)
        previous_statements.insert(1, data)
    elif previous_statements[0]=="" or previous_statements[1]=="":
        logging.info("User provided only one value,Result will be on the basis of single value")
        for items in range(len(previous_statements)):
            data=""
            if previous_statements[items]!="":
                data= previous_statements[items]
            previous_statements.insert(0, data)
            previous_statements.insert(1, data)
    try:
        logging.info("Control inside try block checking if any custom word exists in the query")
        customWordList = customWords
        customWord = False
        resolved = ""
        status = False
        output = {"resolved":resolved,"status": status }
        logging.info("Merging all the previous statemets together")
        for items in range(len(previous_statements)):
           previous_statements[items]= previous_statements[items].rstrip(stripCharacters) 
        
        if len(customWordList)!=0:
            for word in customWordList:
                if word in query.lower():
                    logging.info("Custom is present in the given query")
                    mergedText=""
                    for i in range(len(previous_statements)):
                       mergedText= mergedText+previous_statements[i]+". "
                    tempMergedText =mergedText
                    mergedText = mergedText.title()
                    text = mergedText+"    "+query.lower()+"?"
                    customWord= True

        if customWord:
            logging.info("Applying NLP on the inputs and sperating NOUN and PRONoun form the given INPUTS ")
            doc_text1 = nlp(mergedText)
            doc1_text1= nlp(tempMergedText)
            
            stringList=[]
            list_tokens_text1= [token.text for token in doc_text1 if token.pos_ == "NOUN" or token.pos_ == "PROPN" ]
            list1_tokens_text1 = [token.text for token in doc1_text1]
            logging.info("Noun and pronoun list "+str(list_tokens_text1))

            for word in list1_tokens_text1:
                for nounEle in list_tokens_text1:
                    if word.title() == nounEle or word.lower() == nounEle or word.upper() == nounEle or word == nounEle:
                        stringList.append(word)
            text = unicode_(text)
            doc = nlp(text)
            status = doc._.has_coref            
            if status:
                textR= resolveText(doc,tempMergedText,query,customWord)
                customResolvedtext=customWordResolve(stringList,textR,query)
                resolved = customResolvedtext
                
                if textR == customResolvedtext:
                    resolved = ""
                    status = False
                else:
                    output["resolved"]= resolved.lstrip().rstrip()
                    output["status"]= status 
            logging.info("result "+str(output))
            print(output)
            return output        
        
        else:
            logging.info("no custom word exists on the given query ")
            prevCombinedQuery = ""
            combineLatesQuery =""
            prevLatestQuery =""
            corefStatus = False
            corefStatus13 = False
            corefStatus23 = False
            if previous_statements[0] !="" :
                mergedText =""
                for i in range(len(previous_statements)):
                    mergedText= mergedText+previous_statements[i]+". "
                doc,corefStatus = corefResoultion(mergedText,query)
                doc12,corefStatus12 = corefResoultion(previous_statements[0],previous_statements[1]) 
                doc23,corefStatus23 = corefResoultion(previous_statements[1],query)
                prevCombinedQuery = resolveText(doc,mergedText,query,customWord)
                if corefStatus:
                    prevCombinedQuery = resolveText(doc,mergedText,query,customWord)
                    prevLatestQuery = resolveText(doc12,previous_statements[0],previous_statements[1],customWord)
                    combineLatesQuery =resolveText(doc23,previous_statements[1],query,customWord)
                    if corefStatus12 and corefStatus23:
                        doc223,corefStatus223 =corefResoultion(prevLatestQuery,query)
                        text223 =resolveText(doc223,prevLatestQuery,query,customWord)
                        if corefStatus223:
                            if text223 != query and text223 == prevCombinedQuery:
                                resolved =endCharCheck(query,text223)
                            elif prevCombinedQuery != text223 and combineLatesQuery == query and  prevCombinedQuery != combineLatesQuery:
                                resolved =endCharCheck(query,prevCombinedQuery)
                            elif prevCombinedQuery == combineLatesQuery and combineLatesQuery == query and text223 != query:
                                resolved =endCharCheck(query,text223)
                            elif combineLatesQuery == text223 and prevCombinedQuery != combineLatesQuery :
                                resolved =endCharCheck(query,combineLatesQuery)  

                            else:
                                resolved =endCharCheck(query,prevCombinedQuery)

                        elif corefStatus23 and not(corefStatus12):
                            if combineLatesQuery.rstrip(stripCharacters) == query and prevCombinedQuery !=query:
                                resolved = endCharCheck(query,prevCombinedQuery)
                            else:
                                resolved = endCharCheck(query,combineLatesQuery)

                        else:
                            resolved =""

                    else:
                        if corefStatus23:
                            resolved = endCharCheck(query,combineLatesQuery)

                else:
                    doc,corefStatus = corefResoultion(previous_statements[1],query)  
                    if corefStatus:
                        text = resolveText(doc,previous_statements[1],query,customWord)
                        text= endCharCheck(query,text)
                        resolved = text
                        status = corefStatus                                  
            resolved=resolved.replace(query.lstrip(stripCharacters),"")
            resolvedTemp = resolved.rstrip().lstrip().rstrip(stripCharacters).lstrip(stripCharacters)

            if resolvedTemp == "":
                output["resolved"]= ""
                output["status"]= False
            else:
                output["status"]= True
                output["resolved"]= resolved.lstrip().rstrip()

            print(output)
            logging.info("result "+str(output))
            return output

    except Exception as err:
        output = {"resolved":"","status":"" } 
        output["resolved"]= ""
        output["status"] = False
        logging.error("An error occured: "+str(err)+" affacted output: "+output)
        raise


# %%
#previous_statements = ["what is the job","how to apply job","What are the job requirements"]
#query="how to cancle it"
#evalute_result(previous_statements,query)

# %%
# previous_statements = ["where is China? Where is India?","Where is SINGAPORE? where is newYork?"]
# query="what is difference among them?"
# evalute_result(previous_statements,query)

# %%
# previous_statements = ["how to start the job", ""]
# query="how to cancel it"
# evalute_result(previous_statements,query)

# %%
# previous_statements = []
# query="how to cancel it"
# evalute_result(previous_statements,query)

# %%
# handle the list data (must have 2 elements)
# provide proper nameing convention  for the vars
# approch for the the list items handling - just copy the data of existing item
# kind of Readme.text for installation steps


