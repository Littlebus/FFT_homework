import numpy as np
import cv2
import cmath

class FFTSolver(object):
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.src_img = None
        self.shift_src_img = None
        self.fft_data = None
        self.ifft_data = None
        self.row_index = []
        self.col_index = []
        self.row_weight = []
        self.col_weight = []
        self.top = 0
        self.bottom = 0
        self.left = 0
        self.right = 0

    def dec2bin(self,LEN):
        rs = []
        bit_num = int(np.log2(LEN))
        for i in range(LEN):
            bin_str = bin(i)[2:]
            while len(bin_str) < bit_num:
                bin_str = '0'+bin_str
            rs.append(bin_str)
        return rs
    
    def reverse_bitstr(self,bitstr):
        return bitstr[::-1]
    
    def bin2dec(self,bin_strs):
        LEN = len(bin_strs)
        rs = []
        for bin_str in bin_strs:
            rs.append(int('0b'+bin_str,base=2))
        return rs

    def cal_index(self,LEN):
        idx_strs = self.dec2bin(LEN)
        reversed_idx_strs = [self.reverse_bitstr(bit_str) for bit_str in idx_strs]
        return self.bin2dec(reversed_idx_strs)

    def load_file(self, path):
        self.src_img = cv2.imread(path,cv2.IMREAD_UNCHANGED)
        #self.src_img = cv2.imread(path,cv2.IMREAD_GRAYSCALE)
        #self.src_img = cv2.resize(self.src_img,(256,256))
        
        self.src_img = self.padding(self.src_img)

        self.row_index = self.cal_index(self.src_img.shape[1])
        self.col_index = self.cal_index(self.src_img.shape[0])
    
    def padding(self,img):
        R = img.shape[0]
        C = img.shape[1]
        
        exp_r = np.ceil(np.log2(R))
        exp_c = np.ceil(np.log2(C))
        
        new_R = int(np.power(2,exp_r))
        new_C = int(np.power(2,exp_c))
        self.top = int((new_R - R)/2)
        self.bottom = new_R - R - self.top
        self.left = int((new_C - C)/2)
        self.right = new_C - C - self.left
        return cv2.copyMakeBorder(img,self.top,self.bottom,self.left,self.right,borderType=cv2.BORDER_CONSTANT,value=0)
    
    def one_iteration(self,data,depth):
        result = np.zeros_like(data)
        group_size = int(pow(2,depth))
        stride = int(group_size /2)
        group_num = int(data.shape[0]/group_size)
        if data.shape[0] == len(self.row_index):
            weights = self.row_weight.copy()
        if data.shape[0] == len(self.col_index):
            weights = self.col_weight.copy()
        assert len(weights) == int(data.shape[0]/2),(len(weights),data.shape[0])

        for i in range(group_num):
            start = i * group_size
            for  j in range(int(group_size/2)):
                cur = start + j
                partner = cur + stride
                w_idx = int(j*(data.shape[0]/pow(2,depth)))
                #print(w_idx)
                cur_weight = weights[w_idx]
                result[cur] = data[cur] + data[partner] * cur_weight
                result[partner] = data[cur] - data[partner] * cur_weight
        
        return result

    def fft_one_dimension(self,data):
        idx = []
        #print(data.shape)
        if data.shape[0] == len(self.row_index):
            idx = self.row_index.copy()
        if data.shape[0] == len(self.col_index):
            idx = self.col_index.copy()
        assert len(idx) > 0
        raw_data = [complex(data[i]) for i in idx]
        raw_data = np.array(raw_data,dtype=np.complex64)
        depth = 1
        #print('depth 0: {}'.format(raw_data))
        while int(pow(2,depth)) <= data.shape[0]:
            raw_data = self.one_iteration(raw_data,depth)
            #print('depth {}: {}'.format(depth,raw_data))
            depth += 1 
        
        rs = raw_data.reshape(data.shape)
        #print('output raw_data: {}'.format(rs))
        return rs

        

            

    def fft_channel(self,channel):
        result = np.zeros_like(channel)
        #print('result: {}'.format(result.shape))
        result = result.astype(np.complex64)
        #print(channel.shape)
        #print(result.shape)
        for i in range(channel.shape[0]):
            result[i,:] = self.fft_one_dimension(channel[i,:])
        #print('result after row compute: {}'.format(result))
        for i in range(channel.shape[1]):
            result[:,i] = self.fft_one_dimension(result[:,i])
        #print('result after col compute: {}'.format(result))
            
        return result
    
    def fft(self,img,inverse=False):
        #calculate weights
        if inverse:
            r_exp = complex(0,2*cmath.pi/self.src_img.shape[1])
            c_exp = complex(0,2*cmath.pi/self.src_img.shape[0])
        else:
            r_exp = complex(0,-2*cmath.pi/self.src_img.shape[1])
            c_exp = complex(0,-2*cmath.pi/self.src_img.shape[0])
        r_W = cmath.exp(r_exp)
        c_W = cmath.exp(c_exp)
        #print(self.src_img.shape)
        self.row_weight.clear()
        self.col_weight.clear()
        for i in range(int(self.src_img.shape[1]/2)):
            self.row_weight.append(pow(r_W,i))
        for i in range(int(self.src_img.shape[0]/2)):
            self.col_weight.append(pow(c_W,i))
        #print(len(self.row_weight))
        #print(len(self.col_weight))
        #print(self.src_img.shape)

        assert len(self.row_weight) == int(len(self.row_index) /2), (len(self.row_weight),len(self.row_index))
        
        #print(img.shape)
        if inverse:

            if len(img.shape) == 2:
                self.ifft_data = self.fft_channel(img)
            elif len(img.shape) == 3:
                self.ifft_data = np.zeros_like(self.src_img,dtype=np.complex64)
                for i in range(img.shape[2]):
                    self.ifft_data[:,:,i] = self.fft_channel(img[:,:,i])
            else:
                print('bad input image channel')
                self.ifft_data = None
        
        else:    
            if len(img.shape) == 2:
                self.fft_data = self.fft_channel(img)
            elif len(img.shape) == 3:
                self.fft_data = np.zeros_like(self.src_img,dtype=np.complex64)
                for i in range(img.shape[2]):
                    self.fft_data[:,:,i] = self.fft_channel(img[:,:,i])
            else:
                print('bad input image channel')
                self.fft_data = None
    

    def cvtfft2img_channel(self,channel):
        return np.absolute(channel)


    def cvtfft2img(self,fft_data):
        result = np.zeros(fft_data.shape,dtype=np.float32)
        if len(fft_data.shape) == 2:
            result = self.cvtfft2img_channel(fft_data)
        if len(fft_data.shape) == 3:
            for i in range(fft_data.shape[2]):
                result[:,:,i] = self.cvtfft2img_channel(fft_data[:,:,i])
        
        
        #result = 20*np.log(result + 1)
        #result = result.astype('uint8')
        #print(result.shape)
        return result

    def shift_channel(self,channel):
        '''
        R = channel.shape[0]
        C = channel.shape[1]
        c_row = int(R/2)
        c_col = int(C/2)
        result = np.zeros_like(channel)
        block = channel[0:c_row,0:c_col]
        result[0:c_row,0:c_col] = block[::-1,::-1]
        result[c_row:,0:c_col] = block[:,::-1]
        result[0:c_row,c_col:] = block[::-1,:]
        result[c_row:,c_col:] = block
        return result
        '''
        return np.fft.fftshift(channel)
        
        




    def shift_fft(self):
        #shift_src_img is changed to float
        #self.shift_src_img=np.zeros_like(self.src_img)
        
        result = np.zeros_like(self.fft_data)
        if len(self.src_img.shape) == 2:
            result = self.shift_channel(self.fft_data)
        elif len(self.src_img.shape) == 3:
            for i in range(self.src_img.shape[2]):
                result[:,:,i] = self.shift_channel(self.fft_data[:,:,i])
        else:
            print('bad input image channel')
        return result
            
        
        #print(self.src_img.shape)
        #print(self.shift_src_img.shape)

def fft_and_ifft(path):
    fft_solver = FFTSolver()
    fft_solver.load_file(path)
    #print('src_img shape: {}'.format(fft_solver.src_img.shape))
    #fft
    fft_solver.fft(fft_solver.src_img)
    #print('fft_data shape: {}'.format(fft_solver.fft_data.shape))
    #print('crop option: {}, {}, {}, {}'.format(fft_solver.top,fft_solver.bottom,fft_solver.left,fft_solver.right))
    shifted_fft_data = fft_solver.shift_fft()
    fft_img = fft_solver.cvtfft2img(shifted_fft_data)
    fft_img = 20*np.log(fft_img+ 1)
    fft_img = fft_img.astype('uint8')
    if fft_solver.bottom != 0:
        bottom = -fft_solver.bottom
    else:
        bottom = None
    if fft_solver.right != 0:
        right = -fft_solver.right
    else:
        right = None
    crop_fft_img = fft_img[fft_solver.top:bottom,fft_solver.left:right]
    #ifft
    fft_solver.fft(fft_solver.fft_data,inverse=True)
    ifft_img = fft_solver.cvtfft2img(fft_solver.ifft_data)
    ifft_img = ifft_img/(ifft_img.shape[0]*ifft_img.shape[1])
    ifft_img =ifft_img.astype('uint8')
    crop_ifft_img = ifft_img[fft_solver.top:bottom,fft_solver.left:right]

    return crop_fft_img,crop_ifft_img

        
    


if __name__=='__main__':
    path = './data/15.jpg'
    '''
    fft_img,ifft_img = fft_and_ifft(path)
    cv2.imshow('fft',fft_img)
    cv2.imshow('ifft',ifft_img)
    '''
    
    

    img = cv2.imread(path,cv2.IMREAD_UNCHANGED)
    print(img.shape)
    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)
    fshift = 20*np.log(np.abs(fshift) + 1)
    
    cv2.imshow('cv2',fshift.astype('uint8'))
    cv2.waitKey(0)
    


    