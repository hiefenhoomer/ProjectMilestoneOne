import json


def reformat(item):
    return "'" + str(item) + "',"


def reformat_last(item):
    return "'" + str(item) + "'\n"


def reformat_hours(week, business_id):
    reformatted_items = ''
    for day in week.keys():
        reformatted_items += reformat(business_id) + reformat(day)
        times = week[day].split('-')
        reformatted_items += reformat(times[0]) + reformat_last(str(times[1]))
    return reformatted_items


def reformat_categories(categories, business_id):
    reformatted = ''
    for category in categories:
        reformatted += reformat(business_id) + reformat_last(category)
    return reformatted


def reformat_attributes(attributes, business_id):
    formatted = ''
    for key in attributes.keys():
        item = attributes[key]
        if isinstance(item, dict):
            formatted += reformat_attributes(item, business_id)
        else:
            formatted += reformat(business_id) + reformat(key) + reformat_last(item)
    return formatted


def parse_business():
    count = 0
    print("Parsing business data")
    with open('yelpInput/yelp_business.JSON', 'r') as f_in:
        with open('yelpOutput/business_out.txt', 'w') as f_out:
            for line in f_in:
                count += 1
                item_dict = json.loads(line)

                business_line = reformat(item_dict['name']) + \
                                reformat(item_dict['address']) + reformat(item_dict['city']) + \
                                reformat(item_dict['state']) + reformat(item_dict['postal_code']) + \
                                str(item_dict['latitude']) + ',' + str(item_dict['longitude']) + ',' + \
                                str(item_dict['stars']) + ',' + str(item_dict['review_count']) + ',' + \
                                str(item_dict['is_open']) + '\n'

                business_id = item_dict['business_id']
                business_line += reformat_categories(item_dict['categories'], business_id)
                business_line += reformat_hours(item_dict['hours'], business_id)
                business_line += reformat_attributes(item_dict['attributes'], business_id)


                f_out.write(business_line)
    f_out.close()
    f_in.close()
    print(str(count) + ' businesses parsed')


def hour_frequency(json_line):
    formatted = ''
    for day in json_line['time'].keys():
        for hour in json_line['time'][day]:
            formatted += reformat(json_line['business_id']) + reformat(day) + reformat(hour) + \
                         str(json_line['time'][day][hour]) + '\n'

    return formatted


def parse_checkin():
    count = 0
    with open('yelpInput/yelp_checkin.JSON', 'r') as f_in:
        with open('yelpOutput/checkin_out.txt', 'w') as f_out:
            for line in f_in:
                json_line = json.loads(line)
                freq = hour_frequency(json_line)
                f_out.write(freq)
                count += 1
        f_out.close()
    f_in.close()
    print(str(count) + ' customer days for businesses')


def reformat_text(text):
    reformatted = "'" + text.replace('\n', ' ').replace("'", "''") + "'"
    return reformatted


def parse_review():
    count = 0
    with open('yelpInput/yelp_review.JSON', 'r') as f_in:
        with open('yelpOutput/review_out.txt', 'w') as f_out:
            for line in f_in:
                json_line = json.loads(line)
                reformatted = reformat(json_line['review_id']) + reformat(json_line['user_id']) + \
                    reformat(json_line['business_id']) + str(json_line['stars']) + ',' + reformat(json_line['date']) + \
                    reformat_text(json_line['text']) + ',' + str(json_line['useful']) + ',' + str(json_line['funny']) + \
                    ',' + str(json_line['cool']) + '\n'

                count += 1
                f_out.write(reformatted)
            f_out.close()
        f_in.close()
    print(str(count) + ' reviews parsed')


def parse_user():
    count = 0
    with open('yelpInput/yelp_user.JSON', 'r') as f_in:
        with open('yelpOutput/user_out.txt', 'w') as f_out:
            for line in f_in:
                count += 1
                json_line = json.loads(line)
                formatted = reformat(json_line['user_id']) + reformat(json_line['name']) + \
                            reformat(json_line['yelping_since']) + str(json_line['review_count']) + ',' + \
                            str(json_line['fans']) + ',' + str(json_line['average_stars']) + ',' + \
                            str(json_line['funny']) + ',' + str(json_line['useful']) + ',' + \
                            str(json_line['cool']) + '\n'
                for friend in json_line['friends']:
                    formatted += reformat(json_line['user_id']) + reformat_last(friend)
                f_out.write(formatted)
    f_out.close()
    f_in.close()
    print(str(count) + ' users parsed')



if __name__ == '__main__':
    parse_business()
    parse_checkin()
    parse_review()
    parse_user()
