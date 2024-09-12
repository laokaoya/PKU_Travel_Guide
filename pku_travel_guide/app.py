from flask import Flask, request, jsonify, render_template
import pandas as pd
import os
app = Flask(__name__)
# 加载数据
loc_data = pd.read_csv('templates/data/pku.csv', encoding="utf-8")

# 主页，渲染地图
@app.route('/')
def index():
    # 渲染包含 folium 地图的页面
    return render_template("map/optimized_map.html")

@app.route('/like_location', methods=['POST'])
def like_location():
    data = request.get_json()
    location_name = data['location']
    
    # 加载最新的 CSV 数据
    loc_data = pd.read_csv('templates/data/pku.csv', encoding="utf-8")
    # 更新点赞数
    loc_data.loc[loc_data['location'] == location_name, 'likes'] += 1
    new_likes = loc_data.loc[loc_data['location'] == location_name, 'likes'].values[0]
    # 保存更新到 CSV
    loc_data.to_csv('templates/data/pku.csv', encoding="utf-8-sig", index=False)
    
    return jsonify({'status': 'success','new_likes':int(new_likes)})

@app.route('/rate_location', methods=['POST'])
def rate_location():
    data = request.get_json()
    location_name = data['location']
    new_rating = int(data['rating'])

    # 读取当前数据
    loc_data = pd.read_csv('templates/data/pku.csv', encoding="utf-8-sig")

    # 获取该地点当前的评分和评分次数
    current_ratings = int(loc_data.loc[loc_data['location'] == location_name, 'ratings'].values[0])
    rating_count = int(loc_data.loc[loc_data['location'] == location_name, 'rating_count'].values[0])

    # 计算新的评分
    updated_ratings = (current_ratings * rating_count + new_rating) / (rating_count + 1)
    updated_ratings = round(updated_ratings, 2)  # 保留两位小数
    rating_count += 1

    # 更新数据
    loc_data.loc[loc_data['location'] == location_name, 'ratings'] = updated_ratings
    loc_data.loc[loc_data['location'] == location_name, 'rating_count'] = rating_count

    # 保存回CSV
    loc_data.to_csv('templates/data/pku.csv', encoding="utf-8-sig", index=False)

    # 返回新的评分数据
    return jsonify({'status': 'success', 'new_ratings': updated_ratings})

@app.route('/submit_comment', methods=['POST'])

def submit_comment():
    data = request.get_json()
    location_name = data['location']
    comment = data['comment']
    
    # 读取现有数据
    loc_data = pd.read_csv('templates/data/pku.csv', encoding="utf-8-sig")

    # 获取现有评论
    current_comments = loc_data.loc[loc_data['location'] == location_name, 'comments'].values[0]
    
    # 如果当前评论是NaN，则初始化为空字符串
    if pd.isna(current_comments):
        current_comments = ""
    
    # 将评论字符串分割成列表
    comments_list = current_comments.split(", ") if current_comments else []
    
    # 将新评论加入列表
    comments_list.append(comment)
    
    # 将列表转换回逗号分隔的字符串
    updated_comments = ", ".join(comments_list)
    
    # 更新数据中的评论
    loc_data.loc[loc_data['location'] == location_name, 'comments'] = updated_comments
    
    # 保存回CSV
    loc_data.to_csv('templates/data/pku.csv', encoding="utf-8-sig", index=False)

    return jsonify({'status': 'success'})

@app.route('/get_comments', methods=['GET'])
def get_comments():
    location_name = request.args.get('location')  # 从查询参数获取地点名称
    
    # 读取现有数据
    loc_data = pd.read_csv('templates/data/pku.csv', encoding="utf-8-sig")

    # 获取该地点的评论
    current_comments = loc_data.loc[loc_data['location'] == location_name, 'comments'].values[0]
    
    # 如果没有评论，返回空列表
    if pd.isna(current_comments) or current_comments == "":
        comments_list = []
    else:
        comments_list = current_comments.split(", ")

    return jsonify({'status': 'success', 'comments': comments_list})

if __name__ == '__main__':
    app.run(debug=True)