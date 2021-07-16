import scrapy


class AuthorSpider(scrapy.Spider):
    name = 'sell_house'

    start_urls = ['http://batdongsan.com.vn/ban-nha-rieng/p1']

    def parse(self, response):
        item_page_links = response.css('.wrap-plink')
        yield from response.follow_all(item_page_links, self.parse_item)

        li = response.css('div.pagination a').getall()
        links = response.css('div.pagination a::attr(href)').getall()
        res = li[0]
        for i in li:
            if ('actived' in i):
                res = i
                break
        if li.index(res) < len(li) - 1:
            next_page = links[li.index(res) + 1]
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_item(self, response):
        def area_cal(a):
            a = a.lower()
            return float(a.split('m')[0].strip().replace(',', '.'))

        def price_cal(p, a):
            p = p.lower()
            if ('/m' in p):
                if a == 0:
                    return 0
                else:
                    return float(p.split('triệu')[0].strip().replace(',', '.')) * a
            if ('triệu' in p):
                return float(p.split('triệu')[0].strip().replace(',', '.'))
            if ('tỷ' in p):
                return float(p.split('tỷ')[0].strip().replace(',', '.'))*1000
            return 0

        def bedroom_cal(b):
            b = b.lower()
            return int(b.split('pn')[0].strip())

        def toilet_cal(t):
            t = t.lower()
            return int(t.split(' ')[0].strip())

        def floor_cal(f):
            f = f.lower()
            return int(f.split(' ')[0].strip())

        name = response.css('div.description h1.tile-product::text').get(default='').strip()
        address = response.css('div.description div.short-detail::text').get(default='').strip()
        li = address.split(',')
        city = li[-1].strip().strip('.')
        district = li[-2].strip()

        label1 = response.css('ul.short-detail-2.clearfix.pad-16 li span.sp1::text').getall()
        value1 = response.css('ul.short-detail-2.clearfix.pad-16 li span.sp2::text').getall()
        label1 = [item.strip().lower() for item in label1]
        area = area_cal(value1[label1.index('diện tích:')]) if (label1.count('diện tích:') > 0) else 0
        price = price_cal(value1[label1.index('mức giá:')], area) if (label1.count('mức giá:') > 0) else 0
        bedroom = bedroom_cal(value1[label1.index('phòng ngủ:')]) if (label1.count('phòng ngủ:') > 0) else 0

        label2 = response.css('div.box-round-grey3 div.row-1 span.r1::text').getall()
        label2 = [item.strip().lower() for item in label2]
        value2 = response.css('div.box-round-grey3 div.row-1 span.r2::text').getall()
        value2 = [item.strip() for item in value2]
        toilet = toilet_cal(value2[label2.index('số toilet:')]) if (label2.count('số toilet:') > 0) else 0
        floor = floor_cal(value2[label2.index('số tầng:')]) if (label2.count('số tầng:') > 0) else 0
        house_dir = value2[label2.index('hướng nhà:')] if (label2.count('hướng nhà:') > 0) else ''
        balcony_dir = value2[label2.index('hướng ban công:')] if (label2.count('hướng ban công:') > 0) else ''
        furniture = value2[label2.index('nội thất:')] if (label2.count('nội thất:') > 0) else ''
        law = value2[label2.index('pháp lý:')] if (label2.count('pháp lý:') > 0) else ''
        front = value2[label2.index('mặt tiền:')] if (label2.count('mặt tiền:') > 0) else ''
        road = value2[label2.index('đường vào:')] if (label2.count('đường vào:') > 0) else ''

        label3 = response.css('ul.short-detail-2.list2.clearfix li span.sp1::text').getall()
        label3 = [item.strip().lower() for item in label3]
        value3 = response.css('ul.short-detail-2.list2.clearfix li span.sp3::text').getall()
        value3 = [item.strip() for item in value3]
        post_date = value3[label3.index('ngày đăng:')] if (label3.count('ngày đăng:') > 0) else ''
        expiration_date = value3[label3.index('ngày hết hạn:')] if (label3.count('ngày hết hạn:') > 0) else ''

        des_li = response.css('div.des-product::text').getall()
        des = ''
        for i in des_li:
            des = des + i.strip() + '\n'
        des = des + des + des + des
        imgs = response.css('li.swiper-slide a::attr(style)').getall()
        imgs = [item.split('url(')[1].split(')')[0] for item in imgs]
        imgs = [imgs, imgs, imgs, imgs, imgs]

        yield {
            'name': name,
            'address': address,
            'city': city,
            'district': district,
            'price (million VND)': price,
            'area (m2)': area,
            'bedroom': bedroom,
            "toilet": toilet,
            "floor": floor,
            "front": front,
            "road": road,
            "house direction": house_dir,
            "balcony direction": balcony_dir,
            "furniture": furniture,
            "law": law,
            "post date": post_date,
            "expiration date": expiration_date,
            "description": des,
            "image": imgs
        }