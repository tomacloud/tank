#!/usr/bin/env python
# -*- coding:utf-8 -*-

from lxml import etree as et

from tank import dtutils
from tank.weixin import utils as weixin_utils

class WxBaseWebData():
    def __init__(self):
        self.__dict__["etree"] = et.Element("xml");
        
    def __getattr__(self, name):
        etree = self.__dict__["etree"]
        node = etree.find(name)
        if node is None:
            return ""
        else:
            return node.text

    def __setattr__(self, name, value):
        etree = self.__dict__["etree"]
        node = etree.find(name)

        if node is None:
            node = et.Element(name)
            etree.append(node)

        node.text = value if weixin_utils.is_number(value) else et.CDATA(value)
        
    def __delattr__(self, name):
        etree = self.__dict__["etree"]
        node = etree.find(name)
        if node is not None:
            node.text = ""

    def toString(self):
        return et.tostring(self.__dict__["etree"], encoding = "utf-8")
    
    @classmethod
    def fromString(cls, string):
        data = cls()
        data.__dict__['etree'] = et.fromstring(string)
        return data
    
class WxRequestData(WxBaseWebData): pass

class WxResponseData(WxBaseWebData):
    def __init__(self, to_user_name, from_user_name, msg_type):
        WxBaseWebData.__init__(self)

        self.ToUserName = to_user_name
        self.FromUserName = from_user_name
        self.CreateTime = str(dtutils.now_timestamp())
        self.MsgType = msg_type
        self.FuncFlag = "0"

class WxTextResponseData(WxResponseData):
    def __init__(self, to_user_name, from_user_name, content):
        WxResponseData.__init__(self, to_user_name, from_user_name, "text")
        self.Content = content
        

class WxMusicResponseData(WxResponseData):
    def __init__(self, to_user_name, from_user_name):
        WxResponseData.__init__(self, to_user_name, from_user_name, "music")

    def addMusic(self, title, description, music_url, hq_music_url = None):
        if hq_music_url is None:
            hq_music_url = music_url
            
        music_node = et.Element("Music")
        for tag, text in (("Title", title), ("Description", description), ("MusicUrl", music_url), ("HQMusicUrl", hq_music_url)):
            node = et.Element(tag)
            node.text = text
            music_node.append(node)

        self.__dict__['etree'].append(music_node)

class WxNewsResponseData(WxResponseData):
    def __init__(self, to_user_name, from_user_name):
        WxResponseData.__init__(self, to_user_name, from_user_name, "news")
        
    def setAttr(self, name, value):
        self.__dict__[name] = value
        
    def getAttr(self, name):
        if self.__dict__.has_key(name):
            return self.__dict__[name]
        else:
            return None
    
    def addArticle(self, title, description, pic_url, url):
        article_count = self.getAttr("articlesCount")
        if article_count is None:
            self.initArticleNode()
        else:
            if article_count >= 10:
                print "too much article"
                return
            
            article_count += 1
            self.setAttr("articlesCount", article_count)
            self.__dict__['etree'].find("ArticleCount").text = str(article_count)
        
        article_item = et.Element("item")
        
        if description is None:
            description = ""
            
        if pic_url is None:
            pic_url = ""

        if url is None:
            url = ""
            
        for tag, text in (("Title", title), ("Description", description), ("PicUrl", pic_url), ("Url", url)):
            node = et.Element(tag)
            node.text = et.CDATA(text)
            article_item.append(node)

        self.__dict__['etree'].find("Articles").append(article_item)

    def initArticleNode(self):
        self.setAttr("articlesCount", 1)
        
        article_count = et.Element("ArticleCount")
        article_count.text = "1"
        articles = et.Element("Articles")

        self.__dict__['etree'].append(article_count)
        self.__dict__['etree'].append(articles)
        
    
if __name__ == "__main__":
    xml = "<xml><name>test</name><age>25</age></xml>"
    req_data = WxRequestData.fromString(xml)
    req_data.age = "26"
    print req_data.age

    resp_data = WxNewsResponseData("kona", "weiming")
    resp_data.addArticle("title", "desc", "http://abc.com", "http://def.com")
    resp_data.addArticle("title2", "desc2", "http://abc.com", "http://def.com")
    
    print resp_data.toString()
