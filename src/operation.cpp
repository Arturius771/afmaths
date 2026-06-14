#include "types.h"
#include <functional>
#include <iostream>
#include <vector>

float newtons_raphson_method(float first_term, float function_numerator,
                             float derivative_denominator) {
  return first_term - (function_numerator / derivative_denominator);
}

/**
 * Creates n evenly spaced points between a and b.
 */
std::vector<float> interval(float start, float end, int n) {
  if (n < 2) {
    return {start};
  }

  std::vector<float> values = {};
  float step = step = (end - start) / (n - 1);
  for (int i = 0; i < n; i++) {
    values.push_back(start + i * step);
  }

  return values;
}

/**
 * Calculates the termial of a number (sum of all positive integers up to that
 * number).
 */
int termial(int number) { return ((number + 1) * number) / 2; }

float summation(int start_index, int stop_index, float (*sum_rule)(int)) {
  float total = 0.0;

  for (int i = start_index; i < stop_index + 1; i++) {
    total += sum_rule(i);
  }

  return total;
}

float product(int start_index, int stop_index, float (*product_rule)(int)) {
  float total = 1.0;

  for (int i = start_index; i < stop_index + 1; i++) {
    total *= product_rule(i);
  }

  return total;
}

/**
 * Returns a function that calculates the ratio of num1 to num2.
 */
Ratio ratio(float number1, float number2) { return number1 / number2; }

/**
 * Curried function to return a function that applies a reduction function to a
 * list of values.
 */
std::function<float(std::vector<float>)>
reduce(float (*reduce_function)(float, float)) {
  return [reduce_function](std::vector<float> sequence) -> float {
    // if (sequence.empty()) {
    //   throw std::invalid_argument("Cannot reduce an empty vector");
    // }

    float final_value = sequence[0];

    for (int i = 1; i < sequence.size(); i++) {
      final_value = reduce_function(final_value, sequence[i]);
    }

    return final_value;
  };
}

float add(float a, float b) { return a + b; }

float multiply_by_two(int x) { return x * 2.0f; }

float square(int x) { return x * x; }

int main() {
  std::cout << "=== Newton Raphson ===\n";
  std::cout << newtons_raphson_method(5.0f, 2.0f, 4.0f) << "\n\n";

  std::cout << "=== Interval ===\n";
  std::vector<float> vals = interval(0.0f, 10.0f, 5);

  for (float v : vals) {
    std::cout << v << " ";
  }

  std::cout << "\n\n";

  std::cout << "=== Termial ===\n";
  std::cout << "termial(5) = " << termial(5) << "\n\n";

  std::cout << "=== Summation ===\n";
  std::cout << summation(1, 5, square) << "\n";
  // 1² + 2² + 3² + 4² + 5² = 55

  std::cout << "\n=== Product ===\n";
  std::cout << product(1, 5, multiply_by_two) << "\n";

  std::cout << "\n=== Ratio ===\n";
  std::cout << ratio(10.0f, 4.0f) << "\n";

  std::cout << "\n=== Reduce ===\n";

  auto reducer = reduce(add);

  std::vector<float> numbers = {1, 2, 3, 4, 5};

  std::cout << reducer(numbers) << "\n";

  return 0;
}