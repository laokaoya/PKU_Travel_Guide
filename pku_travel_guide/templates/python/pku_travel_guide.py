#!/usr/bin/env python
# coding: utf-8

# In[1]:


# 找古树
# 找小众
# 找动物
# 找传说
# 找石头
# 找雕塑


# In[2]:


import folium
import pandas as pd
import numpy as np
import tkinter as tk
import math
import webbrowser
import random
import sys
import string
import os
import random
from PIL import Image, ImageDraw, ImageFont
from sklearn.cluster import KMeans
from PyQt5.QtCore import QUrl,QEventLoop, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, \
    QComboBox, QListWidget, QPushButton, QLineEdit, QSizePolicy, QDialog, QDialogButtonBox, QMessageBox, QDesktopWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QPixmap


# In[3]:


# 读取数据
data = pd.read_csv('../data/pku.csv', encoding="utf-8")


# In[4]:


# 计算玩几个景点
def cal_nloc(time_day, interest_type):
    if time_day == '1小时以内':
        num = random.randint(6, 10)
    elif time_day == '1-2小时':
        num = random.randint(10, 15)
    elif time_day == '2-3小时':
        num = random.randint(15, 20)
    elif time_day == '3-5小时':
        num = random.randint(20, 30)
    elif time_day == '5小时以上' :
        num = random.randint(30, 40)

    # 加上起点和终点
    if interest_type == '休闲不累' :
        num = int(num*0.7)
    if interest_type == '带娃旅行' :
        num = int(num*0.9)
    if interest_type == '小众景点' :
        num = int(num*1.1)
    if interest_type == '趣味活动' :
        num = 0
    nloc = num + 2

    return int(nloc)


# In[5]:


def cal_score(selected_clusters, focus, interest_types, nloc, must_visit_attractions):
    # 初始化每个地点的分数
    location_scores = {index: 0 for index, _ in data.iterrows()}       

    # 计算每个地点的分数
    for cluster in selected_clusters:
        cluster_data = data[data['cluster'] == cluster]
        # 聚类内部的地点加分
        for index, row in cluster_data.iterrows():
            location_scores[index] += 500/nloc**2  # 聚类里的地点加分
              
    for index, row in data.iterrows():
        # 必去景点加分
        if row['location'] in must_visit_attractions:
            location_scores[index] += float('inf')
        #感兴趣类型加分
        for option in focus:
            location_scores[index] += row[option] * random.randint(50,100)

        # 设置评价指标
        # 景区热度
        hotscore = (row['counts'])

        # 根据interest设置不同公式
        if interest_types == "经典路线":
            location_scores[index] += hotscore * 3
        elif interest_types == "小众景点":
            location_scores[index] -= 0.5 * hotscore
        elif interest_types == "带娃出游":
            location_scores[index] += 0.5 * hotscore + row['children']*random.randint(50,100)
        elif interest_types == "休闲不累":
            location_scores[index] += hotscore + row['leisure'] * random.randint(50,100)
        elif interest_types == "趣味活动":
            location_scores[index] += hotscore
    
    return location_scores      
    


# In[6]:


def generate_map_based_on_preferences(option_vars, start_loc, end_loc, must_visit_attractions):
    # 创建一个空的列表来存储符合条件的景点
    num_clusters = 6
    filtered_locations = []
    time_day = option_vars['请选择您的计划游玩时间：']
    focus = option_vars['以下表述哪些符合您的游玩目的：']
    interest_types = option_vars['请选择您期望的游玩类型：']
    print(option_vars)
    if '趣味活动：' in option_vars:
        activity=option_vars['趣味活动：']
    nloc = cal_nloc(time_day, interest_types)
    
    # 聚类景点
    locations = np.array(data[['lat', 'lon']])
    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(locations)
    data['cluster'] = kmeans.labels_
    
    # 根据时间天数确定选择的聚类数量
    if time_day == '1小时以内':
        num_selected_clusters = 1
    elif time_day == '1-2小时':
        num_selected_clusters = 2
    elif time_day == '3-5小时':
        num_selected_clusters = 4
    elif time_day == '5小时以上':
        num_selected_clusters = num_clusters
    else:
        num_selected_clusters = num_clusters
    
    # 计算每个聚类中所有元素到起始点的平均距离之和
    avg_distances_to_start = {}
    avg_distances_to_end = {}
    for cluster in range(num_clusters):
        cluster_data = data[data['cluster'] == cluster]
        # 计算到起始点的平均距离
        start_loc_lat_lon = np.array([start_loc['lat'], start_loc['lon']])
        distances_to_start = np.linalg.norm(cluster_data[['lat', 'lon']].values - start_loc_lat_lon, axis=1)
        avg_distances_to_start[cluster] = np.mean(distances_to_start)
        
        # 计算到结束点的平均距离（如果有）
        end_loc_lat_lon = np.array([end_loc['lat'], end_loc['lon']])
        distances_to_end = np.linalg.norm(cluster_data[['lat', 'lon']].values - end_loc_lat_lon, axis=1)
        avg_distances_to_end[cluster] = np.mean(distances_to_end)
            
    # 对平均距离进行排序
    sorted_clusters = sorted(range(num_clusters), key=lambda x: (avg_distances_to_start[x] + avg_distances_to_end[x], avg_distances_to_start[x], avg_distances_to_end[x]))
    
    # 根据时间天数选择最小的聚类
    selected_clusters = sorted_clusters[:num_selected_clusters]
    
    # 计算每个地点的分数
    location_scores = cal_score(selected_clusters, focus, interest_types, nloc, must_visit_attractions)
    
    # 根据分数对地点进行排序
    sorted_locations_by_scores = sorted(location_scores.items(), key=lambda x: x[1], reverse=True)

    
    # 选择得分最高的前 nloc个地点
    for index, score in sorted_locations_by_scores[:(nloc-2)]:
        filtered_locations.append(data.loc[index].to_dict())
    # 输出筛选后的前 nloc 个景点
    return filtered_locations


# In[7]:


class GeneticAlgorithm:
    def __init__(self, locations, kmeans, cluster_color):
        self.locations = locations
        self.num_locations = len(locations)
        self.population_size = 300
        self.mutation_rate = 0.02
        self.num_generations = 6000
        self.kmeans = kmeans
        self.cluster_color = cluster_color

    def generate_initial_population(self):
        population = []
        for _ in range(self.population_size):
            path = random.sample(self.locations, self.num_locations)
            population.append(path)
        return population

    def crossover(self, parent1, parent2):
        crossover_point = random.randint(0, self.num_locations - 1)
        child1 = parent1[:crossover_point] + [loc for loc in parent2 if loc not in parent1[:crossover_point]]
        child2 = parent2[:crossover_point] + [loc for loc in parent1 if loc not in parent2[:crossover_point]]
        return child1, child2

    def mutate(self, path):
        if random.random() < self.mutation_rate:
            idx1, idx2 = random.sample(range(self.num_locations), 2)
            path[idx1], path[idx2] = path[idx2], path[idx1]
        return path

    def calculate_path_length(self, path, start_location, end_location):
        total_distance = 0
        path_with_start_end = [start_location] + path + [end_location]
        for i in range(len(path_with_start_end) - 1):
            total_distance += self.get_distance(path_with_start_end[i], path_with_start_end[i+1])
        return total_distance

    def get_distance(self, loc1, loc2):
        lat1, lon1 = loc1['lat'], loc1['lon']
        lat2, lon2 = loc2['lat'], loc2['lon']
        distance = ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5
        return distance

    def optimize(self, start_location, end_location):
        population = self.generate_initial_population()
        for _ in range(self.num_generations):
            # 选择父代
            parents = random.sample(population, 2)
            parent1, parent2 = parents[0], parents[1]
            # 杂交
            child1, child2 = self.crossover(parent1, parent2)
            # 变异
            child1 = self.mutate(child1)
            child2 = self.mutate(child2)
            # 用子代替换父代
            population.extend([child1, child2])
            # 选择最优个体
            population = sorted(population, key=lambda x: self.calculate_path_length(x, start_location, end_location))[:self.population_size]
        # 去掉起始点和结束点并返回最优个体
        best_path = population[0]
        return best_path


# In[8]:


from difflib import get_close_matches

# 找到最接近的景点名称
def find_closest_locations(non_existing_attractions, all_locations):
    closest_locations = []
    for attraction in non_existing_attractions:
        closest_match = get_close_matches(attraction, all_locations, n=1)
        if closest_match:
            closest_locations.append(closest_match[0])
    return closest_locations

# 读取所有景点
data = pd.read_csv("../data/pku.csv", encoding="utf-8")
all_locations = []
for index, row in data.iterrows():
    all_locations.append(row['location'])


# In[9]:


def read_start_locations():
    # Read locations from start_loc.csv
    start_loc_data = pd.read_csv('../data/start_loc.csv', encoding="utf-8")
    start_locations = list(start_loc_data['location'])
    return start_locations
    
def read_end_locations():
    # Read locations from start_loc.csv
    end_loc_data = pd.read_csv('../data/start_loc.csv', encoding="utf-8")
    end_locations = list(end_loc_data['location'])
    
    return end_locations
    
def linear_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


# In[10]:


import osmnx as ox
import networkx as nx
from folium.plugins import PolyLineTextPath

# 最近邻算法结合道路网的路径生成函数
def nearest_neighbor_route_with_roads(start_node, location_nodes, G):
    current_node = start_node
    tsp_route = [current_node]  # 初始化路径
    unvisited = set(location_nodes)

    while unvisited:
        try:
            # 计算当前节点到每个未访问节点的道路网络距离
            nearest_node = min(unvisited, key=lambda node: nx.shortest_path_length(G, current_node, node, weight='length'))
            
            # 记录路径并将最近的节点标记为已访问
            tsp_route.append(nearest_node)
            unvisited.remove(nearest_node)
            current_node = nearest_node

        except Exception as e:
            print(f"Error accessing node {current_node} or {nearest_node}: {e}")
            break

    return tsp_route

def create_popup_with_interactions(location):
    loc_data=pd.read_csv('../data/pku.csv', encoding="utf-8")
# 获取该地点的信息
    location_name = location['location']
    introduction_text = loc_data.loc[loc_data['location'] == location_name, 'description_academic'].values[0]
    likes = loc_data.loc[loc_data['location'] == location_name, 'likes'].values[0]
    ratings = loc_data.loc[loc_data['location'] == location_name, 'ratings'].values[0]
    
    # 创建HTML内容，包括点赞按钮和评分系统
def create_popup_with_interactions(location):
    loc_data = pd.read_csv('../data/pku.csv', encoding="utf-8")
    
    # 获取该地点的信息
    location_name = location['location']
    introduction_text = loc_data.loc[loc_data['location'] == location_name, 'description_academic'].values[0]
    likes = loc_data.loc[loc_data['location'] == location_name, 'likes'].values[0]
    ratings = loc_data.loc[loc_data['location'] == location_name, 'ratings'].values[0]
    
    # 创建HTML内容，包括点赞按钮和评分系统
    html = f"""
    <div style="font-family: Arial, sans-serif; padding: 10px;">
        <h3 style="font-size:22px; margin-bottom: 10px;">{location_name}</h3>
        <p style="font-size:18px; margin-bottom: 10px;">{introduction_text}</p>
        
        <div style="margin-bottom: 15px;">
            <p id="likes-{location_name}" style="font-size:16px; margin-bottom: 5px;">当前点赞数: {likes}</p>
            <button onclick="likeLocation('{location_name}')" style="font-size:14px; padding: 5px 10px;">点赞</button>
        </div>

        <div style="margin-bottom: 15px;">
            <p id="ratings-{location_name}" style="font-size:16px; margin-bottom: 5px;">当前评分: {ratings}/5</p>
            <label for="rating-select-{location_name}" style="font-size:14px; margin-right: 10px;">请选择评分:</label>
            <select id="rating-select-{location_name}" style="font-size:14px; padding: 5px;">
                <option value="" disabled selected>选择评分</option>
                <option value="1">1</option>
                <option value="2">2</option>
                <option value="3">3</option>
                <option value="4">4</option>
                <option value="5">5</option>
            </select>
            <button onclick="submitRating('{location_name}')" style="font-size:14px; padding: 5px 10px; margin-left: 10px;">提交评分</button>
        </div>

        <div style="margin-bottom: 15px;">
            <textarea id="comment-text-{location_name}" placeholder="输入您的评论" style="width: 100%; height: 60px; font-size:14px; padding: 5px;"></textarea>
            <button onclick="submitComment('{location_name}')" style="font-size:14px; padding: 5px 10px; margin-top: 5px;">提交评论</button>
        </div>
        <!-- 显示评论区域 -->
        <div id="comments-section-{location_name}">
            <button onclick="getComments('{location_name}')">查看评论</button>
            <ul id="comments-list-{location_name}"></ul>
        </div>
    </div>
    """
    return html

# 主函数生成地图
def generate_map(locations, start_location, end_location,select_options):
    data = pd.read_csv('../data/pku.csv', encoding="utf-8")
    # 提取经纬度数据
    coordinates = data[['lat', 'lon']]
    coordinates.columns = ['lat', 'lon']

    # 使用K均值算法进行聚类
    kmeans = KMeans(n_clusters=6, random_state=0).fit(coordinates)

    # 将聚类结果添加到原始数据中
    data['cluster'] = kmeans.labels_

    # 创建颜色字典，将聚类序号映射到颜色
    cluster_color = {cluster: color for cluster, color in zip(range(6), ['red', 'blue', 'green', 'orange', 'purple', 'black'])}
    
    # 使用 osmnx 获取路网数据
    G = ox.graph_from_point((start_location['lat'], start_location['lon']), dist=5000, network_type='walk')

    # 获取起点和终点的最近节点
    try:
        start_node = ox.nearest_nodes(G, start_location['lon'], start_location['lat'])
        end_node = ox.nearest_nodes(G, end_location['lon'], end_location['lat'])
    except Exception as e:
        print(f"Error finding nearest nodes for start or end: {e}")
        return

    # 获取所有地点的最近节点
    location_nodes = []
    for location in locations:
        try:
            loc_node = ox.nearest_nodes(G, location['lon'], location['lat'])
            location_nodes.append(loc_node)
        except Exception as e:
            print(f"Error finding nearest node for location {location['location']}: {e}")

    # 使用最近邻算法结合路网，生成访问顺序
    tsp_route = nearest_neighbor_route_with_roads(start_node, location_nodes, G)
    tsp_route.append(end_node)  # 最后连接终点

    # 创建地图对象
    m = folium.Map(location=[start_location['lat'], start_location['lon']], zoom_start=17)
    interest_type=select_options['请选择您期望的游玩类型：']
    if interest_type=='带娃出游':
        location_introduction = dict(zip(data['location'], data['description_childish']))
    else:
        location_introduction = dict(zip(data['location'], data['description_academic']))
    # 标记起始点
    start_marker = folium.CircleMarker(location=[start_location['lat'], start_location['lon']], radius=12, color='yellow', fill=True, fill_color='yellow', fill_opacity=0.7)
    start_marker.add_to(m)
    
    # 标记结束点
    end_marker = folium.CircleMarker(location=[end_location['lat'], end_location['lon']], radius=12, color='gray', fill=True, fill_color='gray', fill_opacity=0.7)
    end_marker.add_to(m)

    # 添加 locations 的标记
    for location in locations:
        loc = (location['lat'], location['lon'])
        location_name = location['location']
        html1 = create_popup_with_interactions(location)
        # 获取地点的颜色
        cluster = kmeans.predict([[loc[0], loc[1]]])[0]
        color = cluster_color[cluster]

        # 获取地点介绍文本
        introduction_text = location_introduction.get(location_name, "暂无介绍")         
        html = f"""
        <h3 style="font-size:24px;">{location_name}</h3>
        <p style="font-size:20px;">{introduction_text}</p>
        """
        popup = folium.Popup(html1, max_width=400)
    
        # 添加地点标记和弹出框
        folium.Marker(loc, 
                    popup=popup, 
                    icon=folium.Icon(color=color)
                    ).add_to(m)

    # 将每段路径转换为经纬度坐标
    full_route_latlon = []
    
    # 逐段计算基于路网的最短路径
    for i in range(len(tsp_route) - 1):
        try:
            # 计算两个节点之间的最短路径
            route_between_nodes = nx.shortest_path(G, tsp_route[i], tsp_route[i+1], weight='length')
            route_latlon = [(G.nodes[node]['y'], G.nodes[node]['x']) for node in route_between_nodes]
            full_route_latlon.extend(route_latlon)
        except Exception as e:
            print(f"Error calculating path between nodes {tsp_route[i]} and {tsp_route[i+1]}: {e}")
            return

    # 绘制路线并添加方向箭头
    polyline = folium.PolyLine(full_route_latlon, color='blue', weight=5, opacity=0.7)
    polyline.add_to(m)

    # 添加路线方向箭头
    arrow_path = PolyLineTextPath(polyline, '     →     ', repeat=True, offset=10, attributes={'fill': 'red', 'font-weight': 'bold', 'font-size': '32'})
    m.add_child(arrow_path)

    # 将地图保存为HTML文件
    m.save('../map/optimized_map.html')
        # 在地图生成的 HTML 文件中插入 JavaScript 函数
    with open('../map/optimized_map.html', 'a', encoding='utf-8') as f:
        # 写入 JavaScript 函数
        f.write("""
            <script>
            function likeLocation(locationName) {
                // 发送点赞请求到后端
                fetch('/like_location', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 'location': locationName }),
                })
                .then(response => response.json())
                .then(data => {
                    // 获取新的点赞数并更新页面
                    const likesElement = document.getElementById(`likes-${locationName}`);
                    likesElement.textContent = `当前点赞数: ${data.new_likes}`;
                    alert("点赞成功！");
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
            }

            function submitRating(locationName) {
                // 获取用户选择的评分
                const ratingSelect = document.getElementById(`rating-select-${locationName}`);
                const rating = parseInt(ratingSelect.value, 10);

                // 发送评分请求到后端
                fetch('/rate_location', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 'location': locationName, 'rating': rating }),
                })
                .then(response => response.json())
                .then(data => {
                    // 获取新的评分并更新页面
                    const ratingsElement = document.getElementById(`ratings-${locationName}`);
                    ratingsElement.textContent = `当前评分: ${data.new_ratings}/5`;
                    alert("评分成功！");
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
            }
                
            function submitComment(locationName) {
                const commentText = document.getElementById(`comment-text-${locationName}`).value;
                
                if (commentText.trim() === "") {
                    alert("评论不能为空！");
                    return;
                }

                // 发送评论请求到后端
                fetch('/submit_comment', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 'location': locationName, 'comment': commentText }),
                })
                .then(response => response.json())
                .then(data => {
                    alert("评论提交成功！");
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
            }
            function getComments(locationName) {
                // 发送请求获取该地点的评论
                fetch(`/get_comments?location=${locationName}`)
                    .then(response => response.json())
                    .then(data => {
                        const commentsList = document.getElementById(`comments-list-${locationName}`);
                        commentsList.innerHTML = '';  // 清空当前的评论列表

                        // 将每条评论显示出来
                        if (data.comments.length === 0) {
                            commentsList.innerHTML = '<li>暂无评论</li>';
                        } else {
                            data.comments.forEach(comment => {
                                const commentItem = document.createElement('li');
                                commentItem.textContent = comment;
                                commentsList.appendChild(commentItem);
                            });
                        }
                    })
                    .catch((error) => {
                        console.error('Error:', error);
                    });
            }   
            </script>
            """)
class ReorderDialog(QDialog):
    def __init__(self, filtered_locations, parent=None):
        super().__init__(parent)
        self.setWindowTitle('调整推荐景点顺序')
        self.filtered_locations = filtered_locations
        self.reordered_locations = []

        layout = QVBoxLayout(self)

        label = QLabel("拖动以调整景点顺序:")
        layout.addWidget(label)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.list_widget.setDragDropMode(QListWidget.InternalMove)
        self.list_widget.setDefaultDropAction(Qt.MoveAction)

        for location in self.filtered_locations:
            self.list_widget.addItem(location['location'])
        layout.addWidget(self.list_widget)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.on_confirm)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def on_confirm(self):
        self.reordered_locations.clear()
        for i in range(self.list_widget.count()):
            location_name = self.list_widget.item(i).text()
            for location in self.filtered_locations:
                if location['location'] == location_name:
                    self.reordered_locations.append(location)
                    break
        self.accept()

def reorder_recommendations(filtered_locations, parent=None):
    dialog = ReorderDialog(filtered_locations, parent)
    if dialog.exec_() == QDialog.Accepted:
        return dialog.reordered_locations
    return filtered_locations

    
#"燕园古树地图", "燕园动物在哪里", "隐秘的角落", "燕园奇石与雕塑", "那些口口相传的燕园传说", "校内食堂打卡"
def confirm_options(option_vars, right_layout, right_widget):
    selected_options = {}
    for label_text, var in option_vars.items():
        if isinstance(var, QComboBox):
            selected_options[label_text] = var.currentText()
        elif label_text == "请列举您必去的景点（逗号分割）":  
            selected_options[label_text] = var.text()  # Get text from QLineEdit
        else:
            selected_options[label_text] = [item.text() for item in var.selectedItems()]
    # Split the entered text into a list of attractions
    must_visit_attractions = [attraction.strip() for attraction in selected_options.pop("请列举您必去的景点（逗号分割）").split(',')]

    # Check if all attractions exist in loc_information.csv
    loc_data = pd.read_csv('../data/pku.csv', encoding="utf-8")
    non_existing_attractions = [attraction for attraction in must_visit_attractions if attraction not in loc_data['location'].tolist()]


    start = selected_options.pop("起始点：")
    end = selected_options.pop("结束点：")
    
    loc_data = pd.read_csv('../data/start_loc.csv', encoding="utf-8")
    start_loc_filtered = loc_data[loc_data['location'] == start]
    start_location = {
        'location': start_loc_filtered['location'].iloc[0],
        'lat': start_loc_filtered['lat'].iloc[0],
        'lon': start_loc_filtered['lon'].iloc[0]
    }
    
    end_loc_filtered = loc_data[loc_data['location'] == end]
    end_location = {
        'location': end_loc_filtered['location'].iloc[0],
        'lat': end_loc_filtered['lat'].iloc[0],
        'lon': end_loc_filtered['lon'].iloc[0]
    }
    if selected_options['趣味活动：']==[]:
        filtered_locations = generate_map_based_on_preferences(selected_options,start_location,end_location, must_visit_attractions)
            # 调用 reorder_recommendations 函数让用户调整景点顺序
        reordered_locations = reorder_recommendations(filtered_locations)
        generate_map(reordered_locations, start_location, end_location,selected_options)
    else:
        pass
    
    # 删除之前右侧布局中的所有部件
    for i in reversed(range(right_layout.count())):
        widget = right_layout.itemAt(i).widget()
        if widget is not None:
            widget.deleteLater()
    
    # 显示新的地图
    map_view = QWebEngineView()
    #"燕园古树地图", "燕园动物在哪里", "隐秘的角落", "燕园奇石与雕塑", "校内食堂打卡"
    if selected_options['趣味活动：']!=[]:
        if selected_options['趣味活动：']==["燕园古树地图"]:
            map_view.load(QUrl.fromLocalFile(os.path.abspath("../map/tree_map.html")))
        elif selected_options['趣味活动：']==["燕园动物在哪里"]:
            map_view.load(QUrl.fromLocalFile(os.path.abspath("../map/animal_map.html")))
        elif selected_options['趣味活动：']==["隐秘的角落"]:
            map_view.load(QUrl.fromLocalFile(os.path.abspath("../map/hidden_map.html")))
        elif selected_options['趣味活动：']==["燕园奇石与雕塑"]:
            map_view.load(QUrl.fromLocalFile(os.path.abspath("../map/statues_map.html")))
        elif selected_options['趣味活动：']==["校内食堂打卡"]:
            map_view.load(QUrl.fromLocalFile(os.path.abspath("../map/restaurant_map.html")))
        map_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(map_view)
        right_widget.setLayout(right_layout)
    else:
        map_view.load(QUrl.fromUserInput("http://localhost:5000/"))
        map_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(map_view)
        right_widget.setLayout(right_layout)


        # 显示旅游景点选择结果
        route_label = QLabel("推荐的旅游景点:")
        right_layout.addWidget(route_label)
        locations_str = ', '.join([attraction['location'] for attraction in reordered_locations])
        label = QLabel(locations_str)
        right_layout.addWidget(label)

        # 显示错误景点及模糊匹配
        if non_existing_attractions != ['']:
            # Create a label to display the non-existing attractions message
            non_existing_label = QLabel("以下景点不存在:")
            right_layout.addWidget(non_existing_label)
            mistakes_str = ', '.join([attraction for attraction in non_existing_attractions])
            label = QLabel(mistakes_str)
            right_layout.addWidget(label)

            match_label = QLabel("猜您想找: ")
            # 找到最接近的景点
            closest_locations = find_closest_locations(non_existing_attractions, all_locations)
            right_layout.addWidget(match_label)
            closest_str = ', '.join([attraction for attraction in closest_locations])
            label = QLabel(closest_str)
            right_layout.addWidget(label)




# In[20]:


# 验证码生成
def generate_verification_code_image():
    code = ''.join(random.choices(string.digits, k=4))
    image = Image.new('RGB', (100, 40), color = (255, 255, 255))
    font = ImageFont.load_default()
    draw = ImageDraw.Draw(image)
    # 为每个数字设置随机颜色并绘制
    for i, digit in enumerate(code):
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        draw.text((10 + i * 25, 20), digit, font=font, fill=color)  
    image.save("../picture/verifivation_code/verification_code.png")
    return code
def generate_random_guest_name():
    return "游客" + ''.join(random.choices(string.ascii_letters + string.digits, k=10))

class WelcomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("欢迎界面")
        self.setGeometry(200, 200, 600, 600)  # 放大窗口
        
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        
        # 欢迎语和程序介绍
        welcome_label = QLabel("欢迎来到燕园个性化导游系统！")
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        introduction_label = QLabel("在这里，您可以根据您的需求规划北大校园的个性化游玩路线。\n请注册或登录开始使用，或者以游客模式浏览。")
        
        # 添加图片
        pixmap = QPixmap("../picture/welcome_image1.jpg")  # 确保文件路径正确
        image_label = QLabel(self)
        image_label.setPixmap(pixmap)
        image_label.setScaledContents(True)
        image_label.setFixedHeight(400)  # 控制图片高度

        # 创建三个按钮：注册、登录、游客模式
        self.register_button = QPushButton("注册", self)
        self.register_button.clicked.connect(self.show_register_window)
        
        self.login_button = QPushButton("登录", self)
        self.login_button.clicked.connect(self.show_login_window)
        
        self.guest_button = QPushButton("游客模式", self)
        self.guest_button.clicked.connect(self.enter_guest_mode)
        
        layout.addWidget(welcome_label)
        layout.addWidget(introduction_label)
        layout.addWidget(image_label)
        layout.addWidget(self.register_button)
        layout.addWidget(self.login_button)
        layout.addWidget(self.guest_button)
        
        self.setCentralWidget(central_widget)
    
    def show_register_window(self):
        self.register_window = RegisterWindow(self)  # 传递欢迎界面的引用
        self.register_window.show()
        self.close()

    def show_login_window(self):
        self.login_window = LoginWindow(self)  # 传递欢迎界面的引用
        self.login_window.show()
        self.close()

    def enter_guest_mode(self):
        guest_name = generate_random_guest_name()
        QMessageBox.information(self, "游客模式", f"欢迎进入游客模式！您的用户名是：{guest_name}")
        self.open_main_window(guest_name)  # 直接进入主窗口

    def open_main_window(self,username):
        self.main_window = MainWindow(username)  # 打开主窗口
        self.main_window.show()
        self.close()
        
class RegisterWindow(QMainWindow):
    def __init__(self, welcome_window):
        super().__init__()
        self.setWindowTitle("用户注册")
        self.setGeometry(300, 300, 400, 300)
        self.welcome_window = welcome_window  # 保存欢迎界面的引用
        
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)
        
        self.username_label = QLabel("用户名:")
        self.username_input = QLineEdit(self)
        
        self.password_label = QLabel("密码:")
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.confirm_password_label = QLabel("再次输入密码:")
        self.confirm_password_input = QLineEdit(self)
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        self.register_button = QPushButton("注册", self)
        self.register_button.clicked.connect(self.register_user)

        self.back_button = QPushButton("返回", self)  # 返回按钮
        self.back_button.clicked.connect(self.back_to_welcome)
        
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.confirm_password_label)
        layout.addWidget(self.confirm_password_input)
        layout.addWidget(self.register_button)
        layout.addWidget(self.back_button)
        
        self.setCentralWidget(central_widget)
    
    def register_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        if password != confirm_password:
            QMessageBox.warning(self, "注册失败", "两次密码输入不一致！")
            return

        try:
            users_data = pd.read_csv('../data/users.csv')
        except FileNotFoundError:
            users_data = pd.DataFrame(columns=['username', 'password'])

        if username in users_data['username'].values:
            QMessageBox.warning(self, "注册失败", "用户名已存在！")
        else:
            new_user = pd.DataFrame({'username': [username], 'password': [password]})
            users_data = pd.concat([users_data, new_user], ignore_index=True)
            users_data.to_csv('../data/users.csv', index=False)
            QMessageBox.information(self, "注册成功", "用户注册成功！")
            self.back_to_welcome()

    def back_to_welcome(self):
        self.welcome_window.show()
        self.close()

class LoginWindow(QMainWindow):
    def __init__(self, welcome_window):
        super().__init__()
        self.setWindowTitle("用户登录")
        self.setGeometry(300, 300, 400, 300)
        self.welcome_window = welcome_window  # 保存欢迎界面的引用

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        self.username_label = QLabel("用户名:")
        self.username_input = QLineEdit(self)

        self.password_label = QLabel("密码:")
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)

        self.verification_label = QLabel("验证码:")
        self.verification_code = generate_verification_code_image()
        verification_pixmap = QPixmap("../picture/verifivation_code/verification_code.png")
        self.verification_display = QLabel(self)
        self.verification_display.setPixmap(verification_pixmap)
        self.verification_display.setScaledContents(True)
        self.verification_display.setFixedHeight(70)
        self.verification_input = QLineEdit(self)

        self.login_button = QPushButton("登录", self)
        self.login_button.clicked.connect(self.login_user)

        self.back_button = QPushButton("返回", self)  # 返回按钮
        self.back_button.clicked.connect(self.back_to_welcome)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.verification_label)
        layout.addWidget(self.verification_display)
        layout.addWidget(self.verification_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.back_button)

        self.setCentralWidget(central_widget)

    def login_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        entered_code = self.verification_input.text()

        try:
            users_data = pd.read_csv('../data/users.csv')
        except FileNotFoundError:
            QMessageBox.warning(self, "登录失败", "用户数据库不存在！")
            return

        if username not in users_data['username'].values:
            QMessageBox.warning(self, "登录失败", "用户名不存在！")
        elif not str(users_data[users_data['username'] == username]['password'].values[0]) == str(password):
            QMessageBox.warning(self, "登录失败", "密码错误！")
        elif str(entered_code) != str(self.verification_code):
            QMessageBox.warning(self, "登录失败", "验证码错误！")
        else:
            QMessageBox.information(self, "登录成功", f"{username}, 欢迎回来！")
            self.open_main_window(username)

    def back_to_welcome(self):
        self.welcome_window.show()
        self.close()

    def open_main_window(self, username):
        self.main_window = MainWindow(username)  # 打开主窗口
        self.main_window.show()
        self.close()

# 创建主窗口（旅游问卷GUI界面）
class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.setWindowTitle(f"{username}的旅游问卷")
        self.username = username
        screen = QDesktopWidget()
        screen_geometry = screen.availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # 设置窗口的初始大小为屏幕大小
        self.setGeometry(0, 0, screen_width, screen_height-30)

        central_widget = QWidget(self)
        main_layout = QHBoxLayout(central_widget)

        left_widget = QWidget(central_widget)
        left_layout = QVBoxLayout(left_widget)
        left_widget.setFixedWidth(400)

        right_widget = QWidget(central_widget)
        right_layout = QVBoxLayout(right_widget)

        option_widgets = {}

        options = {
            "请选择您的计划游玩时间：": ["1小时以内", "1-2小时", "2-3小时", "3-5小时", "5小时以上"],
            "以下表述哪些符合您的游玩目的：": ["感受学术氛围与文化熏陶", "了解名校往事与名人光辉", "探寻历史遗迹与文物故事", "欣赏山水自然与亭台楼榭", "最高学府打卡并美美拍照"],
            "请选择您期望的游玩类型：": ["经典路线", "小众景点", "带娃出游", "休闲不累", "趣味活动"],
            "趣味活动：": ["燕园古树地图", "燕园动物在哪里", "隐秘的角落", "燕园奇石与雕塑", "校内食堂打卡"],
            "请列举您必去的景点（逗号分割）": "",
            "起始点：": read_start_locations(),
            "结束点：": read_end_locations()
        }

        activity_label = QLabel("趣味活动：")
        activity_list_widget = QListWidget()
        activity_list_widget.setMinimumHeight(150)
        activity_list_widget.setSelectionMode(QListWidget.SingleSelection)
        for activity in options["趣味活动："]:
            activity_list_widget.addItem(activity)
        activity_label.setVisible(False)
        activity_list_widget.setVisible(False)

        for label_text, options_list in options.items():
            label = QLabel(label_text)
            left_layout.addWidget(label)

            if label_text == "以下表述哪些符合您的游玩目的：":
                list_widget = QListWidget()
                list_widget.setMinimumHeight(150)
                list_widget.setSelectionMode(QListWidget.MultiSelection)
                for option in options_list:
                    list_widget.addItem(option)
                left_layout.addWidget(list_widget)
                option_widgets[label_text] = list_widget

            elif label_text == "请选择您期望的游玩类型：":
                combo_box = QComboBox()
                for option in options_list:
                    combo_box.addItem(option)
                left_layout.addWidget(combo_box)
                option_widgets[label_text] = combo_box
                combo_box.currentTextChanged.connect(lambda text: self.toggle_activity_visibility(text, activity_label, activity_list_widget))

            elif label_text == "请列举您必去的景点（逗号分割）":
                line_edit = QLineEdit()
                left_layout.addWidget(line_edit)
                option_widgets[label_text] = line_edit

            else:
                combo_box = QComboBox()
                for option in options_list:
                    combo_box.addItem(option)
                left_layout.addWidget(combo_box)
                option_widgets[label_text] = combo_box

        left_layout.addWidget(activity_label)
        left_layout.addWidget(activity_list_widget)

        confirm_button = QPushButton("确定")
        confirm_button.clicked.connect(lambda: self.confirm_options(option_widgets, right_layout, right_widget))
        left_layout.addWidget(confirm_button)

        main_layout.addWidget(left_widget)

        initial_map_view = QWebEngineView()
        initial_map_view.load(QUrl.fromLocalFile(os.path.abspath("../map/pku_cluster_map.html")))
        initial_map_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout.addWidget(initial_map_view)

        right_widget.setLayout(right_layout)
        main_layout.addWidget(right_widget)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def toggle_activity_visibility(self, selected_text, activity_label, activity_list_widget):
        if selected_text == "趣味活动":
            activity_label.setVisible(True)
            activity_list_widget.setVisible(True)
        else:
            activity_label.setVisible(False)
            activity_list_widget.setVisible(False)

def create_gui():
    app = QApplication(sys.argv)
    welcome_window = WelcomeWindow()
    welcome_window.show()
    sys.exit(app.exec_())

create_gui()


# In[ ]:




