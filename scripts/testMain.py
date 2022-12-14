from PyQt5 import QtWebEngineWidgets
from PyQt5.QtCore import QFile, QIODevice
from PyQt5.QtWidgets import QApplication, QMainWindow
import testUI
import sys
from pyecharts import options as opts
from pyecharts.charts import Map
import pandas as pd

# 输入数据
DATA_PATH = r"../data/DXYArea.csv"
# 输出html路径
MAP_PATH = r"../output/china-covid-map.html"


# 筛选出中国最新的数据，并转化成地图所用形式
def china_data_convert(org_data):
    # 筛选出中国数据
    china_data = org_data[org_data['countryName'] == '中国']
    # 去重 最上面的就是最新的数据
    p_data = china_data.drop_duplicates(subset=['provinceName'], keep="first").reset_index(drop=True)
    p_data = p_data[p_data['provinceName'] != '中国'][['provinceName', 'province_confirmedCount']]
    p_data.rename(columns={'provinceName': 'name', 'province_confirmedCount': 'count'}, inplace=True)
    # 重命名特殊省份
    p_data['name'].replace("宁夏回族自治区", "宁夏", inplace=True)
    p_data['name'].replace("广西壮族自治区", "广西", inplace=True)
    p_data['name'].replace("内蒙古自治区", "内蒙古", inplace=True)
    p_data['name'].replace("新疆维吾尔自治区", "新疆", inplace=True)
    p_data['name'].replace("西藏自治区", "西藏", inplace=True)
    return p_data

def world_data_convert(org_data):
    world_data = org_data[org_data['countryName'] != '中国']
    p_data = world_data.drop_duplicates(subset=['provinceName'], keep="first").reset_index(drop=True)
    p_data = p_data[p_data['provinceName'] != '中国'][['countryEnglishName', 'province_confirmedCount']]
    p_data.rename(columns={'countryEnglishName': 'name', 'province_confirmedCount': 'count'}, inplace=True)
    
    p_data['name'].replace("United States of America", "United States", inplace=True)
    p_data['name'].replace("United States of America", "United States", inplace=True)
    return p_data

# 渲染地图html
def render_map(width, height):
    # 读取并处理数据
    org_data = pd.read_csv(DATA_PATH, encoding='utf-8')  # 初始数据
    c_conv_data = china_data_convert(org_data)
    w_conv_data = world_data_convert(org_data)
    c_list_data = list(zip(list(c_conv_data['name']), list(c_conv_data['count'])))
    w_list_data = list(zip(list(w_conv_data['name']), list(w_conv_data['count'])))
    # 配置地图参数
    mp = Map(
        init_opts=opts.InitOpts(
            chart_id="map",
            width=f"{width-10}px",
            height=f"{height-20}px",
        ),
    )
    mp.add_js_funcs(
        """
        chart_map.on('click', function(params){
            alert(1);
            console.log(params.name);//此处写点击事件内容
        });
        """
    )
    mp.add(
        series_name="各省市确诊人数",
        data_pair=c_list_data,
        maptype="china",
        zoom=1.2,
        # is_roam=False,
        itemstyle_opts={
                # 强调颜色
                "emphasis": {"areaColor": "#CEE5E8"}
            }
    )
    mp.add(
        series_name="各国确诊人数",
        data_pair=w_list_data,
        maptype="world",
        is_selected=False,
        is_map_symbol_show=False,
        zoom=1.2,
        itemstyle_opts={
                # 强调颜色
                "emphasis": {"areaColor": "#CEE5E8"}
            }
    )
    # 关闭标签
    mp.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    mp.set_global_opts(
        visualmap_opts=opts.VisualMapOpts(
            max_=15000,
            range_color=['#FAD4D5','#E50000','#A30000']
        ),
    )
    # 渲染
    mp.render(path=MAP_PATH)
    print("地图已渲染")


if __name__ == '__main__':
    # 创建Qt应用
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    # 注册testUI中的窗口
    ui_components = testUI.Ui_MainWindow()
    ui_components.setupUi(main_window)
    # 渲染地图
    map_view = ui_components.webview
    render_map(map_view.width(), map_view.height())
    map_view.page().settings().setAttribute(QtWebEngineWidgets.QWebEngineSettings.ShowScrollBars, False)
    # 操作窗口所需数据
    html_file = QFile(MAP_PATH)
    html_file.open(QIODevice.ReadOnly)
    html_data = bytes(html_file.readAll()).decode('utf-8')
    map_view.setHtml(html_data)
    # 显示
    main_window.show()
    sys.exit(app.exec_())
