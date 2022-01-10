# %% [markdown]
# # Python期末大作业
# #### 数据爬取与分析

# %%
import requests
from bs4 import BeautifulSoup
import bs4.element
import xlwings as xw
import wordcloud

years=[2019, 2020, 2021]
lst=list()

def getHTMLText(url):
    try:
        r=requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        return r.text
    except:
        print("Error.")

def fillArtcList(ulist, html):
    soup=BeautifulSoup(html, "html.parser")
    for cite in soup.find_all("cite"):
        if (isinstance(cite, bs4.element.Tag)):
            ulist.append(cite.find(class_="title").string)
    del ulist[0] # 第一条不是论文题目

def checkKeyword(ulist, keyword):
    plist=list()
    keyword=keyword.lower()
    for title in ulist:
        if keyword in title.lower():
            plist.append(title)
    return plist

def xlsxWrite(path):
    app=xw.App(visible=False, add_book=False)
    app.display_alerts=False
    app.screen_updating=False
    try:
        wb=app.books.open(path)
    except:
        wb=app.books.add()
    sheet=wb.sheets.active
    for i in range(len(years)):
        head=['A','B','C'][i]+'1'
        sheet.range(head).value=years[i]
        for j in range(len(lst[i])):
            sheet.range(head[0]+str(j+2)).value=lst[i][j]
    wb.save(path)
    wb.close()
    app.quit()

def statistics():
    kv=dict()
    for sublst in lst:
        for title in sublst:
            for word in title.split():
                word=word.lower().strip(",.:-")
                if kv.get(word):
                    kv[word]+=1
                else:
                    kv[word]=1
            for junk in ['a', 'an', 'the', 'of', 'for', 'in', 'on', 'by', 'with', 'from', 'and', 'to']:
                try:
                    del kv[junk]
                except:
                    pass
    srtd=sorted(kv.items(),key=lambda x:x[1], reverse=True)
    with open("stat.txt", "w") as f:
        for col in srtd:
            f.write(col[0]+','+str(col[1])+'\n')
    w=wordcloud.WordCloud(width=1024, height=768, mode="RGBA", background_color=None)
    ukv=dict()
    for k,v in kv.items():
        ukv[k.upper()]=v
    w.generate_from_frequencies(ukv)
    w.to_file("wordcloud.png")
    

# %% [markdown]
# #### main()函数

# %%
def main():
    url_start="https://dblp.uni-trier.de/db/conf/cvpr/cvpr"
    url_end=".html"
    keyword="unsupervised" # 爬取（筛选）关键词
    path="titles.xlsx"
    global lst
    for y in years:
        ulist=list()
        html=getHTMLText(url_start+str(y)+url_end)
        fillArtcList(ulist, html)
        plist=checkKeyword(ulist, keyword)
        print("{0} 年标题包含\"{1}\"的论文共有{2:^6}篇\n".format(y, keyword, len(plist)))
        lst.append(plist)
    xlsxWrite(path)
    statistics()

if __name__=='__main__':
    main()


