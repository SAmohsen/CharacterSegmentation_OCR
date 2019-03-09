import cv2
import os


class Segmentation:
    def __init__(self, img_file):
        self.image = cv2.imread(img_file)
        self.rows = self.image.shape[0]
        self.cols = self.image.shape[1]
        self.line_id = 0
        self.character_id = 0
        self.pre_processing()
        self.segment_in_lines()

    def pre_processing(self):
        # thresh image foreground white and back ground black
        gray_img = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        gray_img = cv2.bitwise_not(gray_img)
        threshold_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        self.image = threshold_img

    def crop_letter(self, start_row, end_row, start_col, end_col):
        cropped_char = self.image[start_row:end_row, start_col:end_col]
        char_name = 'lines/line' + str(self.line_id) + '/line_chars/char' + str(self.character_id) + '.png'
        cv2.imwrite(char_name, cropped_char)

    def crop_line(self, start_row, end_row, start_col, end_col):
        # cropping the image to lines  by slicing the numpy array
        cropped_line = self.image[start_row:end_row, start_col:end_col]
        os.mkdir('lines/line' + str(self.line_id))
        line_name = 'lines/line' + str(self.line_id) + '/line.png'
        cv2.imwrite(line_name, cropped_line)
        # now divide each line to subset of Characters
        os.mkdir('lines/line' + str(self.line_id) + '/line_chars')
        self.segment_in_letters(start_row, end_row, start_col, end_col, cropped_line)

    def track_letter(self, start_col, line_rows, line_cols, cropped_line):
        self.character_id = self.character_id + 1
        c = start_col
        end_char_flag = 0
        while c < line_cols:
            col_sum = 0
            for row in range(line_rows):
                col_sum = col_sum + cropped_line[row][c]

            if col_sum == 0:
                end_char_flag = 1
                break
            else:
                c = c + 1

        if end_char_flag:
            return c

    def track_line(self, row):
        self.line_id = self.line_id + 1
        r = row
        end_line_flag = 0
        while r < self.rows:
            row_sum = 0
            for col in range(self.cols):
                row_sum = row_sum + self.image[r][col]
            if row_sum == 0:
                end_line_flag = 1
                break
            else:
                r = r + 1

        if end_line_flag:
            return r

    def segment_in_letters(self, start_row, end_row, start_col, end_col, cropped_line):
        col = 0
        start__letter_col = start_col
        end_letter_col = end_col
        line_cols = end_col - start_col
        line_rows = end_row - start_row

        while col < line_cols:
            col_sum = 0
            letter_detected = 0
            for row in range(line_rows):
                col_sum = col_sum + cropped_line[row][col]

            if col_sum > 0:
                letter_detected = 1

            if letter_detected:
                start__letter_col = col
                end_letter_col = self.track_letter(start__letter_col, line_rows, line_cols, cropped_line)
                self.crop_letter(start_row, end_row, start__letter_col, end_letter_col)
                col = end_letter_col

            else:
                col = col + 1

    def segment_in_lines(self):
        start_row = 0
        end_row = 0
        start_col = 0
        end_col = self.image.shape[1]
        row = 1
        while row < self.rows:
            line_detected = 0
            row_sum = 0
            for col in range(self.cols):
                row_sum = row_sum + self.image[row][col]

            if row_sum > 0:
                line_detected = 1

            if line_detected:
                start_row = row
                end_row = self.track_line(start_row)
                self.crop_line(start_row, end_row, start_col, end_col)
                row = end_row
            else:
                row = row + 1


if __name__ == '__main__':
    Segmentation('test.png')
