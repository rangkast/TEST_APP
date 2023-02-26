#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#define MIN_THRESHOLD 70
#define MAX_THRESHOLD 255
#define READ 0
#define WRITE 1

typedef struct {
    unsigned char gray;
} Pixel;

typedef struct {
    int width, height;
    Pixel *data;
} Image;

void sharpen(Image *input, Image *output) {
    int width = input->width;
    int height = input->height;
    Pixel *temp = (Pixel *)malloc(width * height * sizeof(Pixel));
    // memset(temp, 0, width * height * sizeof(Pixel));
    int laplacian_kernel[3][3] = {
        {-1, -1, -1},
        {-1,  9, -1},
        {-1, -1, -1}
    };
    int x, y, i, j;
    int sum;

    for (y = 1; y < height - 1; y++) {
        for (x = 1; x < width - 1; x++) {
            sum = 0;
            for (j = 0; j < 3; j++) {
                for (i = 0; i < 3; i++) {
                    sum += laplacian_kernel[j][i] * input->data[(y + j - 1) * width + (x + i - 1)].gray;
                }
            }

            output->data[y * width + x].gray = (unsigned char)fmin(fmax(sum, 0), 255);
            // printf("%d ", output->data[y * output->width + x].gray);
        }
        // printf("\n");
    }
    // Copy the blurred image back to the original image
    // for (i = 1; i < height - 1; i++) {
    //     for (j = 1; j < width - 1; j++) {
    //         input->data[i * width + j] = temp[i * width + j];
    //     }
    // }
    free(temp);
}

void laplacian_filter(Image *input, Image *output) {
    int offset = 1;
    int width = input->width;
    int height = input->height;
    Pixel *temp = (Pixel *)malloc(width * height * sizeof(Pixel));
    // memset(temp, 0, width * height * sizeof(Pixel));

    int laplacian_kernel[3][3] = {
        {-1, -1, -1},
        {-1,  10, -1},
        {-1, -1, -1}
    };
    int i, j, k, l;
    float sum, val;
    for (i = offset; i < height-offset; i++) {
        for (j = offset; j < width-offset; j++) {
            sum = 0.0;
            for (k = -offset; k <= offset; k++) {
                for (l = -offset; l <= offset; l++) {
                    val = input->data[(i + k) * width + (j + l)].gray;
                    sum += val * laplacian_kernel[k + offset][l + offset];
                }
            }
            temp[i * width + j].gray = (unsigned char) fmin(fmax(sum, 0), 255);

        }
    }
    // Copy the blurred image back to the original image
    for (i = offset; i < height - offset; i++) {
        for (j = offset; j < width - offset; j++) {
            input->data[i * width + j] = temp[i * width + j];
        }
    }
    free(temp);
}


void normalize(Image *input) {
    int i;
    unsigned char min = input->data[0].gray;
    unsigned char max = input->data[0].gray;

    for (i = 0; i < input->width * input->height; i++) {
        if (input->data[i].gray < min) {
            min = input->data[i].gray;
        }

        if (input->data[i].gray > max) {
            max = input->data[i].gray;
        }
    }

    for (i = 0; i < input->width * input->height; i++) {
        input->data[i].gray = (unsigned char)(((float)input->data[i].gray - min) / (max - min) * 255);
    }
}


float** make_gaussian_kernel(int kernel_size, float sigma) {
    float** kernel = malloc(kernel_size * sizeof(float*));
    for (int i = 0; i < kernel_size; i++) {
        kernel[i] = malloc(kernel_size * sizeof(float));
    }

    int k = (kernel_size - 1) / 2;
    float sum = 0;
    for (int i = -k; i <= k; i++) {
        for (int j = -k; j <= k; j++) {
            float value = exp(-(i*i + j*j) / (2 * sigma*sigma));
            kernel[i+k][j+k] = value;
            sum += value;
        }
    }

    for (int i = 0; i < kernel_size; i++) {
        for (int j = 0; j < kernel_size; j++) {
            kernel[i][j] /= sum;
        }
    }

    for (int i = 0; i < kernel_size; i++) {
        for (int j = 0; j < kernel_size; j++) {
            printf("%f ", kernel[i][j]);
        }
        printf("\n");
    }

    return kernel;
}


void gaussian_filter(Image *input, Image *output, float** kernel) {
    int i, j, k, l;
    float sum, val;
    int width = input->width;
    int height = input->height;
    // Pixel *temp = (Pixel *)malloc(width * height * sizeof(Pixel));
    // memset(temp, (unsigned char)0.0, width * height * sizeof(Pixel));

    int offset = 1;

    for (i = offset; i < height - offset; i++) {
        for (j = offset; j < width - offset; j++) {
            sum = 0.0;
            // printf("%d ", input[i*width + j]);
            // if (input->data[i*width + j].gray < MIN_THRESHOLD) {
            //     memset(&input->data[i*width + j].gray, 0, sizeof(unsigned char));
            //     continue;
            // }
            for (k = -offset; k <= offset; k++) {
                for (l = -offset; l <= offset; l++) {
                    val = input->data[(i + k) * width + (j + l)].gray;
                    sum += val * kernel[k + offset][l + offset];
                }
            }
            output->data[i * width + j].gray = (unsigned char)sum;
        }
        // printf("\n");
    }

    // for (i = offset; i < height - offset; i++) {
    //     for (j = offset; j < width - offset; j++) {
    //         output->data[i * width + j] = temp[i * width + j];
    //         // printf("%d ", output->data[i * width + j].gray);
    //     }
    // }
    // free(temp);
}


unsigned char* resize_image(unsigned char* input, int input_width, int input_height, int output_width, int output_height) {
    unsigned char *output = (unsigned char *)malloc(1280 * 960 * sizeof(unsigned char));

    for (int y = 0; y < output_height; y++) {
        for (int x = 0; x < output_width; x++) {
            // Compute input pixel coordinates for current output pixel
            float x_input = x * (input_width - 1.0) / (output_width - 1.0);
            float y_input = y * (input_height - 1.0) / (output_height - 1.0);

            // Compute integer and fractional parts of input pixel coordinates
            float x0 = x_input;
            float y0 = y_input;
            float x_frac = x_input - x0;
            float y_frac = y_input - y0;

            // Compute bilinear interpolation of four nearest neighboring pixels
            float pixel_value = 0;
            for (int dy = 0; dy < 2; dy++) {
                for (int dx = 0; dx < 2; dx++) {
                    int x_index = x0 + dx;
                    int y_index = y0 + dy;
                    if (x_index >= 0 && x_index < input_width && y_index >= 0 && y_index < input_height) {
                        float weight = (1.0 - x_frac + dx) * (1.0 - y_frac + dy);
                        pixel_value += input[y_index * input_width + x_index] * weight;
                    }
                }
            }

            // Set output pixel value
            output[y * output_width + x] = pixel_value;
        }
    }

    return output;
}

void file_rw(int rw, Image *input, char* path) {
    FILE *fp = NULL;
    if (rw == READ) {
        fp = fopen(path, "rb");
        fread(input->data, sizeof(Pixel), input->width * input->height, fp);
    } else {
        fp = fopen(path, "wb");
        fwrite(input->data, sizeof(Pixel), input->width * input->height, fp);
    }
    fclose(fp);
}

// Assuming that the input image is a grayscale image with 8-bit per pixel
void unsharp_masking(Image* input_image, Image* output_image, int kernel_size, float amount, float radius)
{
    int width = input_image->width;
    int height = input_image->height;
    // Allocate memory for the blurred image
    Image blurred_image;
    // unsigned char* blurred_image = (unsigned char*)malloc(sizeof(unsigned char) * width * height);
    blurred_image.data = (Pixel *)malloc(width * height * sizeof(Pixel));
    blurred_image.width = width;
    blurred_image.height = height;
    // Blur the input image using a Gaussian filter with the specified radius
    float** kernel = make_gaussian_kernel(kernel_size, radius);
    gaussian_filter(input_image, &blurred_image, kernel);
    free(kernel);

    // memcpy(&blurred_image, input_image, width*height*sizeof(Pixel));
    // for (int i = 1; i < height - 1; i++) {
    //     for (int j = 1; j < width - 1; j++) {
    //         printf("%d ", blurred_image.data[i * width + j].gray);
    //     }
    //     printf("\n");
    // }
    file_rw(WRITE, &blurred_image, "blurred_image.bmp");
    // Subtract the blurred image from the input image to obtain the high-pass filtered image
    // laplacian_filter(&blurred_image);
    for (int i = 0; i < width * height; i++) {
        int high_pass_value = (int)input_image->data[i].gray - (int)blurred_image.data[i].gray;
        high_pass_value = fmax(0, high_pass_value); // Clamp the pixel value to the range [0, 255]
        high_pass_value = fmin(255, high_pass_value);
        output_image->data[i].gray = (unsigned char)high_pass_value;
    }

    // Scale the high-pass filtered image by the specified amount
    for (int i = 0; i < width * height; i++) {
        int scaled_value = (int)input_image->data[i].gray + (int)(amount * ((int)output_image->data[i].gray - (int)input_image->data[i].gray));
        scaled_value = fmax(0, scaled_value); // Clamp the pixel value to the range [0, 255]
        scaled_value = fmin(255, scaled_value);
        output_image->data[i].gray = (unsigned char)scaled_value;
    }

    // Free the memory allocated for the blurred image
    free(blurred_image.data);
}


void filter_threshold(Image *input) {
    int width = input->width;
    int height = input->height;
    int i, j;
    int offset = 1;
    for (i = offset; i < height - offset; i++) {
        for (j = offset; j < width - offset; j++) {
            if (input->data[i*width + j].gray < MIN_THRESHOLD) 
                memset(&input->data[i*width + j].gray, 0, sizeof(unsigned char));
        }
    }
}

int main() {
    Image input, output;
    //unsigned char = 1byte
    //float = 4byte
    input.width = 640;
    input.height = 400;

    input.data = (Pixel*)malloc(input.width * input.height * sizeof(Pixel));

    int i, j;
    // unsigned char *input_image = (unsigned char *)malloc(640 * 400 * sizeof(unsigned char));
    // unsigned char *output_image = (unsigned char *)malloc(640 * 400 * sizeof(unsigned char));
    // Read the image data from a file
    file_rw(READ, &input, "../sync_test/40cm_1/80us/CAM0_2643939471749.bmp");

    // unsigned char *output_image = resize_image(input_image, 640, 400, 1280, 960);

    filter_threshold(&input);

    // // Allocate memory for the output image
    output.width = input.width;
    output.height = input.height;
    output.data = (Pixel*)malloc(output.width * output.height * sizeof(Pixel));
    // // Apply the sharpening filter to the input image


    printf("w:%d h:%d\n", output.width, output.height);
    // float** kernel = make_gaussian_kernel(5, 1.0);
    // gaussian_filter(&input, &output, kernel);
    // free(kernel);
    // laplacian_filter(&input, &output);
    // sharpen(&input, &output);
    // // // Normalize the output image

    unsharp_masking(&input, &output, 5, -1.5, 3.0);
    // normalize(&input);
    file_rw(WRITE, &input, "input.bmp");
    file_rw(WRITE, &output, "output.bmp");

    free(input.data);
    free(output.data);

    return 0;
}
