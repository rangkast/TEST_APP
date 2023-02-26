#include <stdio.h>
#include <stdlib.h>

void resize_image(double* input, int input_width, int input_height,
                  double* output, int output_width, int output_height) {
    for (int y = 0; y < output_height; y++) {
        for (int x = 0; x < output_width; x++) {
            // Compute input pixel coordinates for current output pixel
            double x_input = x * (input_width - 1.0) / (output_width - 1.0);
            double y_input = y * (input_height - 1.0) / (output_height - 1.0);

            // Compute integer and fractional parts of input pixel coordinates
            int x0 = (int) x_input;
            int y0 = (int) y_input;
            double x_frac = x_input - x0;
            double y_frac = y_input - y0;

            // Compute bilinear interpolation of four nearest neighboring pixels
            double pixel_value = 0;
            for (int dy = 0; dy < 2; dy++) {
                for (int dx = 0; dx < 2; dx++) {
                    int x_index = x0 + dx;
                    int y_index = y0 + dy;
                    if (x_index >= 0 && x_index < input_width && y_index >= 0 && y_index < input_height) {
                        double weight = (1.0 - x_frac + dx) * (1.0 - y_frac + dy);
                        pixel_value += input[y_index * input_width + x_index] * weight;
                    }
                }
            }

            // Set output pixel value
            output[y * output_width + x] = pixel_value;
        }
    }
}

int main() {
    int input_width = 3;
    int input_height = 3;
    double input[] = {1, 2, 3, 4, 5, 6, 7, 8, 9};

    int output_width = 6;
    int output_height = 6;
    double* output = malloc(output_width * output_height * sizeof(double));

    resize_image(input, input_width, input_height, output, output_width, output_height);

    for (int y = 0; y < output_height; y++) {
        for (int x = 0; x < output_width; x++) {
            printf("%.2f ", output[y * output_width + x]);
        }
        printf("\n");
    }

    free(output);
    return 0;
}