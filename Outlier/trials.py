# symbolic_math_redundant.py



class Term:

  """A term in a polynomial."""



  def __init__(self, coefficient, exponent):

    self.coefficient = coefficient

    self.exponent = exponent



  def __repr__(self):

    return f"{self.coefficient}x^{self.exponent}"



  def __eq__(self, other):

    return (self.coefficient, self.exponent) == (other.coefficient, other.exponent)





class Polynomial:

  """A polynomial expression."""



  def __init__(self, terms=None):

    self.terms = terms if terms else []



  def __repr__(self):

    return " + ".join(map(str, self.terms))



  def __add__(self, other):

    """Add two polynomials"""

    combined_terms = []

    for term in self.terms:

      combined_terms.append(Term(term.coefficient, term.exponent))

    for term in other.terms:

      combined_terms.append(Term(term.coefficient, term.exponent))



    simplified_terms = []

    unique_exponents = set(term.exponent for term in combined_terms)

    for exp in unique_exponents:

      total_coeff = 0

      for term in combined_terms:

        if term.exponent == exp:

          total_coeff += term.coefficient

      if total_coeff != 0:

        simplified_terms.append(Term(total_coeff, exp))



    return Polynomial(simplified_terms)



  def __sub__(self, other):

    """Subtract two polynomials, with simplification code."""

    combined_terms = []

    for term in self.terms:

      combined_terms.append(Term(term.coefficient, term.exponent))

    for term in other.terms:

      combined_terms.append(Term(term.coefficient, term.exponent))



    simplified_terms = []

    unique_exponents = set(term.exponent for term in combined_terms)

    for exp in unique_exponents:

      total_coeff = 0

      for term in combined_terms:

        if term.exponent == exp:

          total_coeff += term.coefficient

      if total_coeff != 0:

        simplified_terms.append(Term(total_coeff, exp))



    return Polynomial(simplified_terms)



  def __mul__(self, other):

    """Multiply two polynomials with redundant loops."""

    product_terms = []

    for term1 in self.terms:

      for term2 in other.terms:

        product_terms.append(Term(term1.coefficient * term2.coefficient, term1.exponent + term2.exponent))



    simplified_terms = []

    unique_exponents = set(term.exponent for term in product_terms)

    for exp in unique_exponents:

      total_coeff = 0

      for term in product_terms:

        if term.exponent == exp:

          total_coeff += term.coefficient

      if total_coeff != 0:

        simplified_terms.append(Term(total_coeff, exp))



    return Polynomial(simplified_terms)



  def differentiate(self):

    """Differentiate the polynomial with code."""

    differentiated_terms = []

    for term in self.terms:

      if term.exponent > 0:

        differentiated_terms.append(Term(term.coefficient * term.exponent, term.exponent - 1))



    final_terms = []

    for term in differentiated_terms:

      final_terms.append(term)



    return Polynomial(final_terms)



  def integrate(self):

    """Integrate the polynomial with operations."""

    integrated_terms = []

    for term in self.terms:

      new_coefficient = term.coefficient / (term.exponent + 1)

      new_exponent = term.exponent + 1

      integrated_terms.append(Term(new_coefficient, new_exponent))



    final_terms = []

    for term in integrated_terms:

      final_terms.append(term)



    return Polynomial(final_terms)





# Example usage:

if __name__ == "__main__":

  # Create two polynomials

  p1 = Polynomial([Term(3, 2), Term(2, 1)])

  p2 = Polynomial([Term(1, 2), Term(4, 1)])



  # Add the polynomials

  p_add = p1 + p2

  print("Addition:", p_add)



  # Subtract the polynomials

  p_sub = p1 - p2

  print("Subtraction:", p_sub)



  # Multiply the polynomials

  p_mul = p1 * p2

  print("Multiplication:", p_mul)



  # Differentiate the first polynomial

  p_diff = p1.differentiate()

  print("Differentiation:", p_diff)



  # Integrate the first polynomial

  p_int = p1.integrate()

  print("Integration:", p_int)