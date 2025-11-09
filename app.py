import logging
import requests
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as bs
from flask import Flask ,request,render_template,jsonify
logging.basicConfig(filename='scrapper.log',level=logging.INFO)
import pymongo



app=Flask(__name__)

@app.route('/',methods=['POST','GET'])
def homepage():
    return render_template('index.html')
    
@app.route('/review',methods=['POST','GET'])
def index():
    if request.method=='POST':
        try:
            searchString=request.form['content'].replace(' ','')
            url='https://www.flipkart.com/search?q='+searchString
            page_details=uReq(url).read()
            beauty_page=bs(page_details,'html.parser')
            boxes=beauty_page.findAll('div',{'class':'cPHDOP col-12-12'})
            del boxes[0:2]
            page_url='https://www.flipkart.com'+boxes[0].div.div.div.a['href']
            
            page_html=requests.get(page_url)
            page_html.encoding='utf-8'
            b_page_url=bs(page_html.text,'html.parser')
            comments=b_page_url.find_all('div',{'class':'RcXBOT'})

            filename=searchString+'.csv'
            f=open(filename,'w')
            headers='Product,Customer Name,Rating,Heading,Comments '
            f.write(headers)
            reviews=[]

            for i in comments:
                try:
                    name=i.div.findAll('p',{'class':'_2NsDsF AwS1CA'})[0].text
                except:
                    logging.info('name')
                        
                try :
                    rating=i.div.div.div.div.text
                except:
                    rating='no rating'
                    logging.info('name')
                        
                try:
                    commentHead=i.div.div.div.p.text
                except :
                    commentHead='no comment heading'

                try:
                    custComment=i.div.div.findAll('div',{'class':''})[0].div.text
                except Exception as e:
                    logging.info(e)
            
                mydict={'Product':searchString,'Name':name,'Rating':rating,'CommentHead':commentHead,'Comment':custComment}
                reviews.append(mydict)
                
            client=pymongo.MongoClient('mongodb+srv://sknn98885:sknn98885@cluster0.nlozl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
            db=client['review_123']
            review_col=db['review123']
            review_col.insert_many(reviews)
                
            return render_template('result.html',reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)


if __name__=='__main__':
    app.run(host='0.0.0.0')