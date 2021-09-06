import numpy as np
from PIL import Image


class Get_Slide_IMG_Position(object):
    def __init__(self, bg_img_path=None, slide_img_path=None, fullbg_img_path=None) -> None:
        super().__init__()
        self.bg_img_path = bg_img_path
        self.slide_img_path = slide_img_path
        self.fullbg_img_path = fullbg_img_path

    # 比较两张图片的像素点，获得坐标缺口
    def difference_between_bg_fullbg(self):

        # 两张图同时存在则进行处理
        if self.bg_img_path and self.fullbg_img_path:

            # 读取bg所有像素点数组
            bg = Image.open(self.bg_img_path)
            bg_pixel_array = np.asarray(bg)

            # 读取fullbg所有像素点数组
            fullbg = Image.open(self.fullbg_img_path)
            fullbg_pixel_array = np.asarray(fullbg)

            # 图片尺寸
            size = fullbg_pixel_array.shape
            width = size[1]
            height = size[0]

            # 遍历所有像素点
            position = 260
            for row in range(height):  # 遍历每一行
                for col in range(width):  # 遍历每一列

                    # 获取两张图片同一位置的像素点
                    bg_pixel = bg_pixel_array[row, col]
                    fullbg_pixel = fullbg_pixel_array[row, col]

                    # 设置一个Δ值
                    defference = 40
                    # 两张图像素点的r/g/b值之差大于defference则说明找到缺口坐标
                    if abs(int(bg_pixel[0]) - int(fullbg_pixel[0])) > defference and abs(
                            int(bg_pixel[1]) - int(fullbg_pixel[1])) > defference and abs(
                            int(bg_pixel[2]) - int(fullbg_pixel[2])) > defference:
                        if position > col:
                            position, col = col, position
                        # 只需要水平方向的距离，返回position即可
                        return position
        else:
            raise ValueError('缺少bg_img_path或fullbg_img_path参数')

    # 如果没有获取到bg_img_path/fullbg_img_path则单独处理slide_img_path
    def single_img_position(self):
        '''
        思路：
            1.图片灰度化处理后验证码缺口与图片背景会有一个明显边界
                ---》设置边界长度
            2.将图片按照列切割，每列遍历像素点灰度值
                ----》设置灰度区间
            3.同时满足灰度区间+边界值可能就是目标，返回横坐标
        '''
        if self.slide_img_path:
            bg_img_path = self.slide_img_path

            # 读入图片
            bg = Image.open(bg_img_path)
            # 反转像素点保存图片
            bg = bg.convert('L')

            # 保存图片
            bg.save('./static/new_name.png')

            bg_pixel_array = np.asarray(bg)
            # print(bg_pixel_array)

            # 图片尺寸
            size = bg_pixel_array.shape
            width = size[1]

            slide_size = 40  # slide_size图像边界过大或过小都有影响，滑块图片的实际大小的一半比较合适

            # 设置灰度值范围
            '''
            >>>灰度值范围请根据图片边界rgb值确定,Gray=R*0.3+G*0.59+B*0.11     
            '''
            Gray_list = [i for i in range(245, 255)]

            # 遍历拆分出每一列
            '''
            考虑特殊情况：
                1.缺口紧挨滑块;
                2.缺口右侧边缘紧挨背景边缘;
                取值范围可以缩小，不需要全图遍历，
                去掉两侧的极值，即滑块宽度，同时也能排除使用网页截图时最左侧滑块的干扰
            '''
            for w in range(110,width-110):
                store_arr = []
                pix_list = bg_pixel_array[:, w]
                # 遍历一列中每个像素点的灰度值
                for index in range(1, len(pix_list)-1):
                    # 判断每个像素点灰度值范围，且相邻两个灰度值都要在范围内
                    if pix_list[index-1] in Gray_list and pix_list[index] in Gray_list and pix_list[index+1] in Gray_list:
                        # 这里的index为满足灰度范围的像素点的纵坐标
                        store_arr.append(index)
                        # print(pix_list[index])
                if store_arr:
                    # 每遍历一列就用store_arr中纵坐标最大值与最小值之差与slide_size比较
                    if max(store_arr)-min(store_arr) >= slide_size:
                        # 灰度区间与边界值都满足有可能就是目标，返回此时的横坐标
                        return w
            # 全部遍历没有结果
            return None

        else:
            raise ValueError('缺少slide_img_path参数')
