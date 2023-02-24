#include <stdio.h>
#include <stdlib.h>
#include <math.h>

// Define the Gaussian kernel
float kernel[3][3] = {
    {1.0/16, 1.0/8, 1.0/16},
    {1.0/8,  1.0/4, 1.0/8},
    {1.0/16, 1.0/8, 1.0/16}
};

// Function to apply Gaussian blur to an image
void gaussian_blur(unsigned char *image, int width, int height) {
    int i, j, k, l;
    float sum, val;
    unsigned char *temp = (unsigned char *)malloc(width * height * sizeof(unsigned char));
    int offset = 1;
    int kernel_size = 3;

    for (i = offset; i < height - offset; i++) {
        for (j = offset; j < width - offset; j++) {
            sum = 0.0;
            for (k = -offset; k <= offset; k++) {
                for (l = -offset; l <= offset; l++) {
                    val = image[(i + k) * width + (j + l)];
                    sum += val * kernel[k + offset][l + offset];
                }
            }
            temp[i * width + j] = (unsigned char)sum;
        }
    }

    // Copy the blurred image back to the original image
    for (i = offset; i < height - offset; i++) {
        for (j = offset; j < width - offset; j++) {
            image[i * width + j] = temp[i * width + j];
        }
    }

    free(temp);
}

int main() {
    int width = 640;
    int height = 400;
    int i, j;
    unsigned char *image = (unsigned char *)malloc(width * height * sizeof(unsigned char));

    // Read the image data from a file
    FILE *fp = fopen("./sync_test/40cm_1/80us/CAM0_2643939471749.bmp", "rb");
    fread(image, sizeof(unsigned char), width * height, fp);
    fclose(fp);

    // Apply Gaussian blur to the image
    gaussian_blur(image, width, height);

    // Write the blurred image data to a file
    FILE *fp2 = fopen("./sync_test/40cm_1/80us/CAM0_2643939471749_blur.bmp", "wb");
    fwrite(image, sizeof(unsigned char), width * height, fp2);
    fclose(fp2);

    free(image);

    return 0;
}
