import scrapy
#import cfscrape
#from fake_useragent import UserAgent
from .decoder import Decoder


class QuotesSpider(scrapy.Spider):
    name = "hemnet"


    def start_requests(self):
        url = 'https://www.hemnet.se/bostader?location_ids%5B%5D=17755&item_types%5B%5D=bostadsratt'
        yield scrapy.Request(url=url, callback=self.parse)



    def parse(self, response):
        for ad in response.css("ul.normal-results > li.js-normal-list-item > a::attr('href')"):
            adUrl = ad.get()
            #ua = UserAgent(cache=False)
            #token, agent = cfscrape.get_tokens(adUrl, ua['google chrome'])
            #yield scrapy.Request(url=adUrl, cookies=token, headers={'User-Agent': agent}, callback=self.parseAd)
            yield scrapy.Request(url=adUrl, callback=self.parseAd)


        nextPage = response.css("a.next_page::attr('href')").get()
        if nextPage is not None:
            yield response.follow(nextPage, callback=self.parse)



    def parseAd(self, response):
        hemnetUrl = response.request.url
        address = response.css("div.property-info__primary-container > div.property-info__address-container > div.property-address > h1.property-address__street::text").get()
        area = response.css("div.property-info__primary-container > div.property-info__address-container > div.property-address > div.property-address__area-container > span.property-address__area::text").get()

        price = response.css("div.property-info__primary-container > div.property-info__price-container > p.qa-property-price::text").get()
        price = price.replace('kr', '')
        price = price.replace(u'\xa0', '')
        
        attrData = {}
        for attr in response.css("div.property-info__attributes-and-description > div.property-attributes > div.property-attributes-table > dl.property-attributes-table__area > div.property-attributes-table__row"):
            attrLabel = attr.css("dt.property-attributes-table__label::text").get()
            attrValue = attr.css("dd.property-attributes-table__value::text").get()
            if attrLabel != None:
                if attrLabel == "Förening":
                    attrValue = attr.css("dd.property-attributes-table__value > div.property-attributes-table__housing-cooperative-name > span.property-attributes-table__value::text").get()
                
                attrValue = attrValue.replace(u'\xa0', '')
                attrValue = attrValue.replace(u'\n', '')
                attrValue = attrValue.replace(u'\t', '')
                attrValue = attrValue.replace('kr/mån', '')
                attrValue = attrValue.replace('kr/år', '')
                attrValue = attrValue.replace('kr/m²', '')
                attrValue = attrValue.replace('m²', '')
                attrValue = attrValue.strip()

                attrData[attrLabel] = attrValue




        description = ""
        for descr in response.css("div.property-description--long > p"):
            descrTxt = descr.css("p::text").get()
            if descrTxt != None and descrTxt != "":
                description = description + "\n" + descrTxt




        agencyUrl = response.css("a.property-description-broker-button::attr('href')").get()


        showings = {}
        i = 0
        for showing in response.css("ul.listing-showings__list > li"):
            showingTime = showing.css("div.listing-showings__showing-info > span.listing-showings__showing-time::text").get()
            showingTime = showingTime.replace(u'\xa0', '')
            showingTime = showingTime.replace(u'\n', '')
            showingTime = showingTime.replace(u'\t', '')
            showingTime = showingTime.strip()

            showingDesc = showing.css("div.listing-showings__showing-description::text").get()
            showingDesc = showingDesc.replace(u'\xa0', '')
            showingDesc = showingDesc.replace(u'\n', '')
            showingDesc = showingDesc.replace(u'\t', '')
            showingDesc = showingDesc.strip()
            
            showings[i] = {
                "time": showingTime,
                "description": showingDesc
            }
            i = i + 1
            


        for broker in response.css("div.broker-contact-card__information > p"):
            brokerName = broker.css("strong::text").get()
            if brokerName != None:
                brokerName = brokerName.replace(u'\xa0', '')
                brokerName = brokerName.replace(u'\n', '')
                brokerName = brokerName.replace(u'\t', '')
                brokerName = brokerName.strip()
                
            brokerLink = broker.css("a.broker-link::attr('href')").get()
            if brokerLink != None:
                brokerLink = brokerLink.replace(u'\xa0', '')
                brokerLink = brokerLink.replace(u'\n', '')
                brokerLink = brokerLink.replace(u'\t', '')
                brokerLink = brokerLink.strip()

            brokerCompany = broker.css("a.broker-link::text").get()
            if brokerCompany != None:
                brokerCompany = brokerCompany.replace(u'\xa0', '')
                brokerCompany = brokerCompany.replace(u'\n', '')
                brokerCompany = brokerCompany.replace(u'\t', '')
                brokerCompany = brokerCompany.strip()



        for brokerContact in response.css("div.broker-contact-card__information > div.broker-contacts > p"):
            brokerPhone = brokerContact.css("span.broker-contact__info-container > span.broker-contact__info > a.broker-contact__link::attr('href')").get()
            if brokerPhone.find("tel:") != -1:
                brokerPhone = brokerPhone.replace("tel:", "")
                brokerPhone = brokerPhone.replace(u'\xa0', '')
                brokerPhone = brokerPhone.replace(u'\n', '')
                brokerPhone = brokerPhone.replace(u'\t', '')
                brokerPhone = brokerPhone.strip()
            

        #          ***The broker email is sometimes None, check the reason later***
            brokerEmail = brokerContact.css("span.__cf_email__::attr('data-cfemail')").get()
            if brokerEmail != None:
                brokerEmail = Decoder.decodeEmail(brokerEmail)
                brokerEmail = brokerEmail.replace(u'\xa0', '')
                brokerEmail = brokerEmail.replace(u'\n', '')
                brokerEmail = brokerEmail.replace(u'\t', '')
                brokerEmail = brokerEmail.strip()











            