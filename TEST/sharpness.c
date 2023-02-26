#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    unsigned char gray;
} Pixel;

typedef struct {
    int width, height;
    Pixel *data;
} Image;

void sharpen(Image *input, Image *output) {
    int kernel[3][3] = {
        {-1, -1, -1},
        {-1,  9, -1},
        {-1, -1, -1}
    };
    int x, y, i, j;
    int sum;

    for (y = 1; y < input->height - 1; y++) {
        for (x = 1; x < input->width - 1; x++) {
            sum = 0;
            for (j = 0; j < 3; j++) {
                for (i = 0; i < 3; i++) {
                    sum += kernel[j][i] * input->data[(y + j - 1) * input->width + (x + i - 1)].gray;
                }
            }

            output->data[y * output->width + x].gray = (unsigned char)fmin(fmax(sum, 0), 255);
        }
    }
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
        input->data[i].gray = (unsigned char)(((double)input->data[i].gray - min) / (max - min) * 255);
    }
}

int main() {
    Image input, output;
    int x, y;
    input.width = 640;
    input.height = 400;

    // Load the input image
    FILE *fp = fopen("../sync_test/40cm_1/80us/CAM0_2643939471749.bmp", "rb");
    input.data = (Pixel*)malloc(input.width * input.height * sizeof(Pixel));
    fread(input.data, sizeof(Pixel), input.width * input.height, fp);
    fclose(fp);

    // Allocate memory for the output image
    output.width = input.width;
    output.height = input.height;
    output.data = (Pixel*)malloc(output.width * output.height * sizeof(Pixel));

    // Apply the sharpening filter to the input image
    sharpen(&input, &output);

    // Normalize the output image
    normalize(&output);

    FILE *fp2 = fopen("CAM0_2643939471749_sharpness_normalize.bmp", "wb");
    fwrite(output.data, sizeof(Pixel), output.width * output.height, fp2);
    fclose(fp2);

    free(input.data);
    free(output.data);

    return 0;
}
    

