'''
Created on Jan 26, 2012

@package: Newscoop
@copyright: 2011 Sourcefabric o.p.s.
@license: http://www.gnu.org/licenses/gpl-3.0.txt
@author: Gabriel Nistor

Provides unit testing for the encoder and decoder xml.
'''

from .. import __setup__
from ..samples.api.article import Article
from ..samples.api.article_type import ArticleType
from ..samples.impl.article import ArticleService
from ..samples.impl.article_type import ArticleTypeService
from ..test_support import ResponseTest, EncoderPathTest
from ally.api.configure import modelFor
from ally.api.type import Iter, Type
from ally.container import ioc, aop
from ally.core.spec.resources import ResourcesManager, Path
from ally.core.spec.server import Processors, Request
import re
import unittest

# --------------------------------------------------------------------

class TestEncoderXML(unittest.TestCase):
        
    def testEncoderXML(self):
        assembly = ioc.open(aop.modulesIn(__setup__))
        get = assembly.processForPartialName
        try:
            services = get('services')
            assert isinstance(services, list)
            services.append(ArticleTypeService())
            services.append(ArticleService())
            
            resourcesManager = get('resourcesManager')
            assert isinstance(resourcesManager, ResourcesManager)
            
            converterPath = get('converterPath')
            
            processors = get('encoderXMLProcessors')
            assert isinstance(processors, Processors)
            
            processorMeta = get('encoderCreateMetaProcessors')
            assert isinstance(processorMeta, Processors)
            
            processorText = get('encoderTextXMLProcessors')
            assert isinstance(processorText, Processors)
            
            req, rsp = Request(), ResponseTest()
            rsp.contentConverter = converterPath
            rsp.encoderPath = EncoderPathTest(converterPath)
            rsp.objMeta = None
            
            # Test Property convert
            
            rsp.obj, rsp.objType = 1, Article.Id
            req.resourcePath = resourcesManager.findResourcePath(converterPath, ['Article', '1'])
            processors.newChain().process(req, rsp)
            xml = str(rsp.wfile.getvalue(), 'utf8')
            self.assertTrue(re.sub('[\s]+', '', xml) == re.sub('[\s]+', '',
'''<?xml version="1.0" encoding="UTF-8"?>
<Article href="Article/1"><Id>1</Id></Article>'''))
            
            rsp.obj, rsp.objType = 'The Name', Article.Name
            processors.newChain().process(req, rsp)
            xml = str(rsp.wfile.getvalue(), 'utf8')
            self.assertTrue(re.sub('[\s]+', '', xml) == re.sub('[\s]+', '',
'''<?xml version="1.0" encoding="UTF-8"?>
<Article><Name>The Name</Name></Article>'''))
            
            # Test Model encoding
            
            a = Article()
            a.Id, a.Name, a.Type = 1, 'Article 1', 2
            rsp.obj, rsp.objType = a, modelFor(Article).type
            req.resourcePath = resourcesManager.findResourcePath(converterPath, ['Article', '1'])
            processors.newChain().process(req, rsp)
            xml = str(rsp.wfile.getvalue(), 'utf8')
            self.assertTrue(re.sub('[\s]+', '', xml) == re.sub('[\s]+', '',
'''<?xml version="1.0" encoding="UTF-8"?>
<Article href="Article/1"><Type href="ArticleType/2"><Id>2</Id></Type><Id>1</Id><Name>Article 1</Name></Article>'''))
            
#            processorMeta.newChain().process(req, rsp)
#            del rsp.objMeta['Type']
#            processorText.newChain().process(req, rsp)
#            xml = str(rsp.wfile.getvalue(), 'utf8')
#            self.assertTrue(re.sub('[\s]+', '', xml) == re.sub('[\s]+', '',
#'''<?xml version="1.0" encoding="UTF-8"?>
#<Article><Id>1</Id><Name>Article 1</Name></Article>'''))
#            
#            processorMeta.newChain().process(req, rsp)
#            del rsp.objMeta['Name']
#            processorText.newChain().process(req, rsp)
#            xml = str(rsp.wfile.getvalue(), 'utf8')
#            self.assertTrue(re.sub('[\s]+', '', xml) == re.sub('[\s]+', '',
#'''<?xml version="1.0" encoding="UTF-8"?>
#<Article><Type href="ArticleType/2">2</Type><Id>1</Id></Article>'''))
#            
#            processorMeta.newChain().process(req, rsp)
#            del rsp.objMeta['Type']
#            del rsp.objMeta['Name']
#            processorText.newChain().process(req, rsp)
#            xml = str(rsp.wfile.getvalue(), 'utf8')
#            self.assertTrue(re.sub('[\s]+', '', xml) == re.sub('[\s]+', '',
#'''<?xml version="1.0" encoding="UTF-8"?>
#<Id>1</Id>'''))
            
            a = Article()
            a.Id, a.Name, a.Type = 3, 'Article 3', 4
            rsp.obj, rsp.objType = a, modelFor(Article).type
            req.resourcePath = resourcesManager.findResourcePath(converterPath, ['Article', '1'])
            processors.newChain().process(req, rsp)
            xml = str(rsp.wfile.getvalue(), 'utf8')
            self.assertTrue(re.sub('[\s]+', '', xml) == re.sub('[\s]+', '',
'''<?xml version="1.0" encoding="UTF-8"?>
<Article href="Article/3"><Type href="ArticleType/4"><Id>4</Id></Type><Id>3</Id><Name>Article 3</Name></Article>'''))
            
            at = ArticleType()
            at.Id, at.Name = 1, 'Article Type 1'
            rsp.obj, rsp.objType = at, modelFor(ArticleType).type
            req.resourcePath = resourcesManager.findResourcePath(converterPath, ['ArticleType', '1'])
            processors.newChain().process(req, rsp)
            xml = str(rsp.wfile.getvalue(), 'utf8')
            self.assertTrue(re.sub('[\s]+', '', xml) == re.sub('[\s]+', '',
'''<?xml version="1.0" encoding="UTF-8"?>
<ArticleType href="ArticleType/1"><Article href="ArticleType/1/Article"/><Id>1</Id><Name>Article Type 1</Name>'''\
'</ArticleType>'))
            
            # Test list paths encoding
            
            rsp.obj, rsp.objType = resourcesManager.findGetAllAccessible(), Iter(Type(Path))
            processors.newChain().process(req, rsp)
            xml = str(rsp.wfile.getvalue(), 'utf8')
            self.assertTrue(re.sub('[\s]+', '', xml) == re.sub('[\s]+', '',
'''<?xml version="1.0" encoding="UTF-8"?>
<Resources><ArticleType href="ArticleType"/><Article href="Article"/></Resources>'''))
            
            # Test list property encoding
            
            rsp.obj, rsp.objType = [1, 2], Iter(Article.Id)
            req.resourcePath = resourcesManager.findResourcePath(converterPath, ['Article'])
            processors.newChain().process(req, rsp)
            xml = str(rsp.wfile.getvalue(), 'utf8')
            self.assertTrue(re.sub('[\s]+', '', xml) == re.sub('[\s]+', '',
'''<?xml version="1.0" encoding="UTF-8"?>
<ArticleList><Article href="Article/1"><Id>1</Id></Article><Article href="Article/2"><Id>2</Id></Article>'''\
'</ArticleList>'))
            
            rsp.obj, rsp.objType = [1, 2], Iter(Article.Type)
            processors.newChain().process(req, rsp)
            xml = str(rsp.wfile.getvalue(), 'utf8')
            self.assertTrue(re.sub('[\s]+', '', xml) == re.sub('[\s]+', '',
'''<?xml version="1.0" encoding="UTF-8"?>
<ArticleList><Article><Type href="ArticleType/1"><Id>1</Id></Type></Article><Article><Type href="ArticleType/2">'''\
'<Id>2</Id></Type></Article></ArticleList>'))
            
            rsp.obj, rsp.objType = ['The Hulk 1', 'The Hulk 2'], Iter(Article.Name)
            processors.newChain().process(req, rsp)
            xml = str(rsp.wfile.getvalue(), 'utf8')
            self.assertTrue(re.sub('[\s]+', '', xml) == re.sub('[\s]+', '',
'''<?xml version="1.0" encoding="UTF-8"?>
<ArticleList><Article><Name>The Hulk 1</Name></Article><Article><Name>The Hulk 2</Name></Article></ArticleList>'''))
            
            # Test list models encoding
            
            a1, a2 = Article(), Article()
            a1.Id, a1.Name, a1.Type = 1, 'Article 1', 1
            a2.Id, a2.Name, a2.Type = 2, 'Article 2', 2
            rsp.obj, rsp.objType = (a1, a2), Iter(Article)
            req.resourcePath = resourcesManager.findResourcePath(converterPath, ['Article'])
            processors.newChain().process(req, rsp)
            xml = str(rsp.wfile.getvalue(), 'utf8')
            self.assertTrue(re.sub('[\s]+', '', xml) == re.sub('[\s]+', '',
'''<?xml version="1.0" encoding="UTF-8"?>
<ArticleList>'''\
'<Article href="Article/1"><Type href="ArticleType/1"><Id>1</Id></Type><Id>1</Id><Name>Article 1</Name></Article>'\
'<Article href="Article/2"><Type href="ArticleType/2"><Id>2</Id></Type><Id>2</Id><Name>Article 2</Name></Article>'\
'</ArticleList>'))
            
#            processorMeta.newChain().process(req, rsp)
#            del rsp.objMeta.metaItem['Type']
#            del rsp.objMeta.metaItem['Name']
#            rsp.objMeta.metaItem['Id'] = rsp.objMeta.metaItem['Id'].metaLink
#            processorText.newChain().process(req, rsp)
#            xml = str(rsp.wfile.getvalue(), 'utf8')
#            self.assertTrue(re.sub('[\s]+', '', xml) == re.sub('[\s]+', '',
#'''<?xml version="1.0" encoding="UTF-8"?>
#<ArticleList><Article href="Article/1"/><Article href="Article/2"/></ArticleList>'''))
#            
#            processorMeta.newChain().process(req, rsp)
#            del rsp.objMeta.metaItem['Id']
#            del rsp.objMeta.metaItem['Name']
#            processorText.newChain().process(req, rsp)
#            xml = str(rsp.wfile.getvalue(), 'utf8')
#            self.assertTrue(re.sub('[\s]+', '', xml) == re.sub('[\s]+', '',
#'''<?xml version="1.0" encoding="UTF-8"?>
#<ArticleList><Article><Type href="ArticleType/1">1</Type></Article><Article><Type href="ArticleType/2">2</Type>'''\
#'</Article></ArticleList>'))
            
            rsp.obj, rsp.objType = {'Type': {'href': 'ArticleType/2', 'Id': '2'}, 'Id': '1'}, None
            rsp.objMeta = req.resourcePath = None
            processors.newChain().process(req, rsp)
            xml = str(rsp.wfile.getvalue(), 'utf8')
            self.assertTrue(re.sub('[\s]+', '', xml) == re.sub('[\s]+', '',
'''<?xml version="1.0" encoding="UTF-8"?>
<Type><href>ArticleType/2</href><Id>2</Id></Type><Id>1</Id>'''))
            
        finally: ioc.close()

# --------------------------------------------------------------------
  
if __name__ == '__main__':
    unittest.main()