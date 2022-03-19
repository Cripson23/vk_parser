from flask import Flask, request, jsonify
from vk_parsing import VkCommentsParsing

app = Flask(__name__)


@app.route("/vkparsing/comments", methods=['POST'])
def get_comments():
    domains = request.json['domains']
    date_start = request.json['date_start']
    comments = VkCommentsParsing().get_all_comments_text(domains, date_start)

    if not request.json or not 'domains' in request.json or not 'date_start' in request.json:
        abort(400)

    response = jsonify(
        message="Success",
        statusCode=200,
        data={
        'domains': domains,
        'date_start': date_start,
        'comments': comments
    })

    return response


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)