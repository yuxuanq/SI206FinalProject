## Your name: Yuxuan Qiu
## The option you've chosen: Option 3

# Put import statements you expect to need here!
import scrapy
import re


class MathCourseSpider(scrapy.Spider):
    name = "math"

    def start_requests(self):
        urls = ['http://www.lsa.umich.edu/cg/cg_results.aspx?termArray=w_17_2120&cgtype=ug&show=100&department=MATH&iPageNum=1',
                'http://www.lsa.umich.edu/cg/cg_results.aspx?termArray=w_17_2120&cgtype=ug&show=100&department=MATH&iPageNum=2',
                'http://www.lsa.umich.edu/cg/cg_results.aspx?termArray=w_17_2120&cgtype=ug&show=100&department=MATH&iPageNum=3',]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        for course in response.css('div.ClassRow'):
            math = str(course.css('div.col-sm-12 font::text').extract())
            instructor = course.css('div.col-sm-3 a::text').extract()
            section = course.css('div.col-sm-3::text').extract()
            email = course.css('div.col-sm-3 a::attr(href)').extract()
            yield {"course_name" : math, "sec":section, "instructor":instructor,"email":email}


