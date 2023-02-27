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
    int width;
    int height;
    Pixel *data;
} Image;

void laplacian_filter(Image *input, Image *output) {
    int offset = 1;
    int width = input->width;
    int height = input->height;
    float laplacian[3][3] = {
        { -1,  -1, -1 },
        { -1, 10,  -1 },
        { -1,  -1, -1 }
    };
    int i, j, k, l;
    float sum, val;
    for (i = offset; i < height-offset; i++) {
        for (j = offset; j < width-offset; j++) {
            sum = 0.0;
            for (k = -offset; k <= offset; k++) {
                for (l = -offset; l <= offset; l++) {
                    val = input->data[(i + k) * width + (j + l)].gray;
                    sum += val * laplacian[k + offset][l + offset];
                }
            }
            memset(&output->data[i*width + j].gray, (unsigned char)fmin(fmax(0, sum), 255), sizeof(Pixel));
        }
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
    int offset = 1;

    // memcpy(output, input, sizeof(input));

    // int cmp = memcmp(input, output, sizeof(input));
    // if (cmp == 0) {
    //     printf("The arrays are equal.\n");
    // } else {
    //     printf("The arrays are not equal.\n");
    // }
    // Pixel *temp = (Pixel *)malloc(width * height * sizeof(Pixel));
    for (i = offset; i < height - offset; i++) {
        for (j = offset; j < width - offset; j++) {
            sum = 0.0;
            for (k = -offset; k <= offset; k++) {
                for (l = -offset; l <= offset; l++) {
                    val = input->data[(i + k) * width + (j + l)].gray;
                    sum += val * kernel[k + offset][l + offset];
                }
            }
            memset(&output->data[i*width + j].gray, (unsigned char)fmin(fmax(0, sum), 255), sizeof(Pixel));
        }
    }
//     for (i = offset; i < height - offset; i++) {
//         for (j = offset; j < width - offset; j++) {
//             output->data[i * width + j] = temp[i * width + j];
//         }
//     }
//     free(temp);
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


void filter_threshold(Image *input, int threshold) {
    int width = input->width;
    int height = input->height;
    int i, j;
    int offset = 1;
    for (i = offset; i < height - offset; i++) {
        for (j = offset; j < width - offset; j++) {
            if (input->data[i*width + j].gray < threshold) 
                memset(&input->data[i*width + j].gray, (unsigned char)0.0, sizeof(Pixel));
        }
    }
}


void increase_grayscale_sharpness(Image *input, Image *output, int kernel_size, float weight1, float weight2, float radius) {
    float** kernel = make_gaussian_kernel(kernel_size, radius);
    int width = input->width;
    int height = input->height;
    gaussian_filter(input, output, kernel);
    free(kernel);
    Image blurr_image;
    blurr_image.data = (Pixel*)malloc(width * height * sizeof(Pixel));
    memcpy(&blurr_image, output, sizeof(blurr_image));
    laplacian_filter(&blurr_image, output);

    int i, j;
    int offset = 1;
    for (i = offset; i < height - offset; i++) {
        for (j = offset; j < width - offset; j++) {
            float scaled_value = (float)(weight1*input->data[i*width + j].gray) + (float)(weight2 * (output->data[i*width + j].gray));            
            scaled_value = fmin(fmax(0, scaled_value), 255);
            memset(&output->data[i*width + j].gray, (unsigned char)scaled_value, sizeof(Pixel));
        }
    }
}


void unsharp_masking(Image* input_image, Image* output_image, int kernel_size, float amount, float radius)
{
    int width = input_image->width;
    int height = input_image->height;
   
    // Blur the input image using a Gaussian filter with the specified radius
    float** kernel = make_gaussian_kernel(kernel_size, radius);
    gaussian_filter(input_image, output_image, kernel);
    free(kernel);
    file_rw(WRITE, output_image, "blurred_output_image.bmp");

    int i, j;
    int offset = 1;
    for (i = offset; i < height - offset; i++) {
        for (j = offset; j < width - offset; j++) {
            float high_pass_value = (float)input_image->data[i*width + j].gray - (float)output_image->data[i*width + j].gray;
            high_pass_value = fmin(fmax(0, high_pass_value), 255);
            memset(&output_image->data[i*width + j].gray, (unsigned char)high_pass_value, sizeof(Pixel));
        }
    }
    
    for (i = offset; i < height - offset; i++) {
        for (j = offset; j < width - offset; j++) {
            float scaled_value = (float)input_image->data[i*width + j].gray + (float)(amount * (float)(output_image->data[i*width + j].gray - input_image->data[i*width + j].gray));            
            scaled_value = fmin(fmax(0, scaled_value), 255);
            memset(&output_image->data[i*width + j].gray, (unsigned char)scaled_value, sizeof(Pixel));
        }
    }
}

void gaussain_added(Image *input, Image *output, int kernel_size, float weight1, float weight2, float radius) {
    float** kernel = make_gaussian_kernel(kernel_size, radius);
    int width = input->width;
    int height = input->height;
    gaussian_filter(input, output, kernel);
    free(kernel);

    Image sharpen_image;
    sharpen_image.data = (Pixel*)malloc(width * height * sizeof(Pixel));
    // memcpy(&sharpen_image, input, sizeof(sharpen_image));
    laplacian_filter(output, &sharpen_image);

    int offset = 1;
    for (int i = offset; i < height - offset; i++) {
        for (int j = offset; j < width - offset; j++) {
            float scaled_value = (float)output->data[i*width + j].gray * weight1 + (float)sharpen_image.data[i*width + j].gray * weight2;
            scaled_value = fmin(fmax(0, scaled_value), 255);
            memset(&output->data[i*width + j].gray, (unsigned char)scaled_value, sizeof(Pixel));            
        }
    }
}

int main() {
    Image input, output;
    char *path[] = {
        "../sync_test/40cm_1/80us/CAM0_2643939471749.bmp",
        "../sync_test/40cm_1/50us/CAM0_1065748889956.bmp",        
        "../sync_test/20cm_1/100us/CAM0_50696563155398.bmp",        
    };
    char *PATH = path[0];
    input.width = 640;
    input.height = 400;
    input.data = (Pixel*)malloc(input.width * input.height * sizeof(Pixel));
    file_rw(READ, &input, PATH);
    filter_threshold(&input, MIN_THRESHOLD);
    output.width = 640;
    output.height = 400;
    output.data = (Pixel*)malloc(output.width * output.height * sizeof(Pixel));
    file_rw(READ, &output, PATH);
    filter_threshold(&output, MIN_THRESHOLD);


    /* idea 1*/
    gaussain_added(&input, &output, 5, 1.5, 1.0, 3.0);
    /* idea 2 */
    // increase_grayscale_sharpness(&input, &output, 5, 1.0, 0.5, 3.0);
    /* idea 3*/
    // unsharp_masking(&input, &output, 5, -1.5, 3.0); 

    file_rw(WRITE, &input, "input.bmp");
    file_rw(WRITE, &output, "output.bmp");

    free(input.data);
    free(output.data);

    return 0;
}
