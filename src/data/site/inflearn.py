import re
import requests
from scrapy import Selector

from sites import Site


class Inflearn(Site):
    def __init__(self):
        super().__init__()

        self.site_name = "inflearn"

    def get_page_info(self, url):
        page = requests.get(url).text
        resp = Selector(text=page).response

        main_thumbnail_img = resp.xpath(".//div[@class='cd-header__thumbnail ']/img/@src").get()
        course_title = resp.xpath(".//div[@class='cd-header__title']/text()").get()

        curriculum = resp.xpath(".//section[@class='cd-curriculum']")
        curriculum_header = curriculum.xpath(".//span[@class='cd-curriculum__sub-title']/text()").get().split("\n")

        #TODO: if this not need variable because its probably useless
        total_count = re.sub(r"[^\d]", "", curriculum_header[0])
        total_time = re.search(r"(\d+)시간(?:\s+)?(\d+)분", curriculum_header[1]).groups()
        total_time = f"{total_time[0]}시간{total_time[1]}분"

        contents = curriculum.xpath(".//div[@class='cd-accordion__section-cover']")

        result = {
            "title": course_title,
            "img": main_thumbnail_img,
            "total_count" : total_count,
            "total_time" : total_time,
            "contents": []
        }
        for content in contents:

            section_title = content.xpath(".//span[@class='cd-accordion__section-title']/text()").get()
            # include number of lectures, running_time
            section_info = content.xpath(".//span[@class='cd-accordion__section-info']/text()").get()

            section_info = re.search(r"(\d+)(?:[\s\S]+)?강(?:[\s\S]+)?(\d+시간)?\s(\d+분)?", section_info).groups()

            lecture_numbers = f"{section_info[0]}강"

            # TODO: check to represent hour
            section_running_time = f"{section_info[1] if section_info[1] else ''} {section_info[2]}".strip()
            section_contents = content.xpath(".//*[@class='cd-accordion__unit']")

            section = {
                "section_title": section_title,
                "section_info": section_info,
                "section_running_time": section_running_time,
                "units": []
            }

            for unit in section_contents:
                unit_title = unit.xpath(".//span[@class='ac-accordion__unit-title']/text()").get()
                unit_running_time = unit.xpath(".//span[@class='ac-accordion__unit-info--time']/text()").get()
                unit_running_time = unit_running_time if unit_running_time else "00:00"

                # TODO: should to check what screen status if user login
                is_preview = unit.xpath(".//span[@class='ac-accordion__unit-info--preview']/text()").get()
                is_preview = True if is_preview else False

                preview_href = unit.xpath("@href").get()
                preview_href = preview_href if preview_href else ""

                unit_info = {
                    "unit_title": unit_title,
                    "unit_running_time": unit_running_time,
                    "is_preview": is_preview,
                    "preview_href": preview_href
                }
                section["units"].append(unit_info)

            result["contents"].append(section)
        return result


if __name__ == '__main__':
    url = "https://www.inflearn.com/course/%EC%8A%A4%ED%94%84%EB%A7%81-%ED%95%B5%EC%8B%AC-%EC%9B%90%EB%A6%AC-%EA%B3%A0%EA%B8%89%ED%8E%B8#curriculum"
    i = Inflearn()
    i.get_page_info(url)
