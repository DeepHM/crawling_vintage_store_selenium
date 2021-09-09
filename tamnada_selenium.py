import os
import time
from time import sleep
from datetime import datetime , timedelta

import pandas as pd
import re
import json

from selenium import webdriver

def matching_cat(cat) :
    print('matching_cat :',cat)
    # outer, top, bottom, skirt, dress, others
    res = ''
    if cat == 'OUTWEAR' :
        res = 'outer'
    if cat == 'KNIT&CARDICAN' :
        res = 'top'
    if cat == 'TOP' :
        res = 'top'
    if cat == 'DRESS' :
        res = 'dress'
    if cat == 'SLIP ' :
        res = 'others'
    if cat == 'BOTTOM' :
        res = 'bottom'
        
    return res

def get_size(text,split_string) :
    print('get_size :',text)
    text=text.replace(split_string,'').split(' ')
    text=[i for i in text if i!='']
    
    size = {}
    for i,s in enumerate(text) :
        if i%2==0 :
            size[s] = 0 
            key = s
        else :
            size[key] = s
            
    if '가슴' in size.keys() :
        size['chest'] = size.pop('가슴')
    if '허리' in size.keys() :
        size['waist'] = size.pop('허리')
            
    for i in list(size.keys()) :
        if (i!='chest') and (i!='waist') :
            del size[i]
        else :
            try :
                size[i] = str(size[i])
            except :
                del size[i]
    

    return size

def brand_match(brand,brandlist) :
    print('brand_match :',brand)
    if any(brandlist.iloc[:,1].str.contains(brand)) :
        brand_matching = brandlist.iloc[:,0][brandlist.iloc[:,1].str.contains(brand).tolist().index(True)]
    elif any(brandlist.iloc[:,2].str.contains(brand)) :
        brand_matching = brandlist.iloc[:,0][brandlist.iloc[:,2].str.contains(brand).tolist().index(True)]
    elif any(brandlist.iloc[:,3].str.contains(brand)) :
        brand_matching = brandlist.iloc[:,0][brandlist.iloc[:,3].str.contains(brand).tolist().index(True)]
    elif any(brandlist.iloc[:,4].str.contains(brand)) :
        brand_matching = brandlist.iloc[:,0][brandlist.iloc[:,4].str.contains(brand).tolist().index(True)]
    else :
        brand_matching = 'etc'
    
    return brand_matching



def main() : 
    chrome_options = webdriver.ChromeOptions()
    ## timed out error opt
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("enable-automation")
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-infobars")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-browser-side-navigation")
    chrome_options.add_argument("--disable-gpu")
    ## server run opt
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    brandlist=pd.read_csv('brandlist.csv',keep_default_na=False)

    storeName = '탐나다'
    cats = {'women_OUTWEAR' : ['https://tamnada.co.kr/product/list.html?cate_no=24&page=',9],
            'women_KNIT&CARDICAN' : ['https://tamnada.co.kr/product/list.html?cate_no=26&page=',12],
            'women_TOP' : ['https://tamnada.co.kr/product/list.html?cate_no=27&page=',63],
            'women_DRESS' : ['https://tamnada.co.kr/product/list.html?cate_no=68&page=',16],
            'women_SLIP' : ['https://tamnada.co.kr/product/list.html?cate_no=368&page=',10],
            'women_BOTTOM' : ['https://tamnada.co.kr/product/list.html?cate_no=42&page=',24],

            'men_OUTWEAR' : ['https://tamnada.co.kr/product/list.html?cate_no=111&page=',6],
            'men_KNIT&CARDICAN' : ['https://tamnada.co.kr/product/list.html?cate_no=60&page=',5],
            'men_TOP' : ['https://tamnada.co.kr/product/list.html?cate_no=49&page=',40],
            'men_BOTTOM' : ['https://tamnada.co.kr/product/list.html?cate_no=332&page=',11] 
           }
    print(cats)
    print('len(category) :',len(cats))


    start = time.time()
    for c in range(len(cats)) :
        cat = list(cats.keys())[c]
        pages = list(cats.values())[c][1]
        pages = list(range(1,pages+1))    

        if not os.path.exists('/'.join([storeName,cat])) :
            os.makedirs('/'.join([storeName,cat]), exist_ok=True)   

        cat_start = time.time()
        n_iter = 1
        for p in pages : 
            # main page connect
            driver = webdriver.Chrome('./chromedriver',chrome_options=chrome_options)
            main_url = list(cats.values())[c][0] + str(p)
            driver.get(main_url)

    #         item_count = len(driver.find_elements_by_class_name("thumb"))
            item_count=len(driver.find_elements_by_css_selector('#itsp1 > ul >li'))
            print(f'category : {cat}   page : {p}/{len(pages)} item_count : {item_count}','\n')

            time.sleep(0.5)   

            n = 1
            page_start = time.time()
            for t in range(1,item_count+1) :

                isSoldOut = f'/html/body/div[2]/div[3]/div[2]/div/div[2]/div/ul/li[{t}]/div/div[2]'
                isSoldOut = driver.find_element_by_xpath(isSoldOut).find_element_by_class_name('icon > .promotion')
                try : 
                    isSoldOut.find_element_by_tag_name('img')
                    isSoldOut = True
                except : 
                    isSoldOut = False


                item = f'/html/body/div[2]/div[3]/div[2]/div/div[2]/div/ul/li[{t}]/div/div[2]/strong/a/span[2]'
                item = driver.find_element_by_xpath(item)
                item.click()
                time.sleep(0.5)

                contentUrl = driver.current_url


                name = driver.find_element_by_class_name('name').text
                name = name.replace("\n"," ")
                #storeName = storeName
                category = matching_cat(cat.split('_')[-1])
                gender = cat.split('_')[0]
                brand = driver.find_element_by_class_name('cont').text.replace("\n"," ")
                brand = re.search(r'브랜드 :(.*?)컨디션 :', brand).group(1).replace(" ","").lower()
                brand = ''.join(filter(str.isalnum, brand)) 
                brand = brand_match(brand,brandlist)
                originalPrice = driver.find_element_by_id('span_product_price_text').text
                originalPrice = str(''.join(re.findall('\d+', originalPrice)))
                salePrice = driver.find_element_by_id('span_product_price_sale').text
                salePrice = salePrice[:salePrice.find('(')]
                salePrice = str(''.join(re.findall('\d+', salePrice)))
                thumbnailUrl = driver.find_elements_by_xpath('//*[@id="contents"]/div[2]/div[1]/div[1]/div[1]/div[1]/div/img')[0].get_attribute('src')
                # contentUrl
                # isSoldOut
                sizes = driver.find_element_by_class_name('cont').text.replace("\n"," ")
                sizes = re.search(r'실측길이(.*?)권장사이즈', sizes).group(1).replace("( cm ) ","")
                size = get_size(sizes,':')

                result = {
                        "name":name,
                        "storeName":storeName,
                        "category":category,
                        "gender":gender,
                        "brand":brand,
                        "originalPrice":originalPrice,
                        "salePrice":salePrice,
                        "thumbnailUrl":thumbnailUrl,
                        "contentUrl":contentUrl,
                        "isSoldOut":isSoldOut,
                        "size":size
                    }

                file_name='/'.join([storeName,cat,'page'+str(p)+'_'+str(n)+'.json'])
                with open(file_name, "w") as json_file:
                    json.dump(result, json_file)

                print('files',cat,n_iter)
                print(result)
                print()
                if n%50 == 0 :
                    print()
                    print(f'category : {cat}   page - [{p}-{n}]  n_files : {n_iter}')
                    print(result)
                    page_run_time = timedelta(seconds=time.time() - page_start)
                    print('Average - runtime : ',page_run_time.seconds/n,' seconds')
                    print('category run time : ', "{:0>8}".format(str(timedelta(seconds=time.time() - cat_start))))
                    print('Total run time : ', "{:0>8}".format(str(timedelta(seconds=time.time() - start))))
                    print()

                n+=1
                n_iter +=1

                driver.back()

            time.sleep(0.5)    
            driver.quit()

        print(f'------------ END : {cat}')
        print('category run time : ', "{:0>8}".format(str(timedelta(seconds=time.time() - cat_start))))



    print('END !!!!!!!!!!!!!!')


if __name__ == '__main__' :
    main()

























