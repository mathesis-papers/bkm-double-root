import argparse
import json
from math import comb


def require(condition, message):
    if not condition:
        raise ValueError(message)


def normalized(coefficients):
    result = list(coefficients)
    while result and result[-1] == 0:
        result.pop()
    return tuple(result)


def remainder(coefficients, divisor):
    result = list(normalized(coefficients))
    require(divisor[-1] == 1, 'The divisor must be monic.')
    while len(result) >= len(divisor):
        factor = result[-1]
        offset = len(result) - len(divisor)
        for index, coefficient in enumerate(divisor):
            result[offset + index] -= factor * coefficient
        result = list(normalized(result))
    return tuple(result)


def polynomial_children(polynomial, divisor):
    added = list(polynomial) if polynomial else [0]
    added[0] += 1
    multiplied = (0,) + polynomial
    return remainder(added, divisor), remainder(multiplied, divisor)


def polynomial_shells(divisor, depth):
    seen = {()}
    shell = {()}
    yield shell, seen
    for generation in range(1, depth + 1):
        candidates = set()
        for polynomial in shell:
            candidates.update(polynomial_children(polynomial, divisor))
        shell = candidates - seen
        seen.update(shell)
        yield shell, seen


def double_coordinates(polynomial):
    return sum(polynomial), sum(index * value for index, value in enumerate(polynomial))


def simple_coordinates(polynomial):
    return (polynomial[1] if len(polynomial) > 1 else 0,
            polynomial[0] if polynomial else 0)


def check_universal(depth):
    shell = {()}
    seen = {()}
    checked = 0
    for generation in range(depth + 1):
        expected = 1 if generation == 0 else 2 ** (generation - 1)
        require(len(shell) == expected, 'Universal-tree cardinality mismatch.')
        for polynomial in shell:
            if polynomial:
                require(sum(polynomial) + len(polynomial) - 1 == generation,
                        'Universal-tree distance mismatch.')
            reduced = remainder(polynomial, (1, -2, 1))
            require(double_coordinates(reduced) == double_coordinates(polynomial),
                    'Value-and-derivative reduction mismatch.')
            checked += 1
        candidates = set()
        for polynomial in shell:
            added = list(polynomial) if polynomial else [0]
            added[0] += 1
            candidates.add(normalized(added))
            candidates.add(normalized((0,) + polynomial))
        shell = candidates - seen
        seen.update(shell)
    return checked


def check_double(depth):
    counts = []
    pair_seen = {(0, 0)}
    pair_shell = {(0, 0)}
    for generation, (shell, seen) in enumerate(polynomial_shells((1, -2, 1), depth)):
        coordinates = {double_coordinates(polynomial) for polynomial in shell}
        require(coordinates == pair_shell, 'Polynomial and pair generations differ.')
        expected_shell = {(0, 0)} if generation == 0 else {(generation, 0)} | {
            (first, second)
            for first in range(1, generation)
            for second in range(first * (generation - first - 1) + 1,
                                first * (generation - first) + 1)}
        require(coordinates == expected_shell, 'Double-root generation formula differs.')
        require(len(shell) == 1 + generation * (generation - 1) // 2,
                'Double-root cardinality mismatch.')
        require(len(seen) == 1 + generation + comb(generation + 1, 3),
                'Accumulated-set cardinality mismatch.')
        for first, second in coordinates:
            if first:
                require(first + (second + first - 1) // first == generation,
                        'Double-root distance mismatch.')
        counts.append(len(shell))
        if generation >= 3:
            require(counts[-1] == 3 * counts[-2] - 3 * counts[-3] + counts[-4],
                    'Double-root recurrence mismatch.')
        pair_candidates = {(first + 1, second) for first, second in pair_shell}
        pair_candidates.update((first, second + first) for first, second in pair_shell)
        pair_shell = pair_candidates - pair_seen
        pair_seen.update(pair_shell)
    require(counts[:11] == [1, 1, 2, 4, 7, 11, 16, 22, 29, 37, 46],
            'Double-root Table 5 entries differ.')
    return {'depth': depth, 'residues': len(seen), 'initial_counts': counts[:11],
            'shells_equal': True, 'distances_equal': True, 'recurrence_from': 3}


def check_simple(depth):
    counts = []
    for generation, (shell, seen) in enumerate(polynomial_shells((-1, 0, 1), depth)):
        coordinates = {simple_coordinates(polynomial) for polynomial in shell}
        expected_shell = {(0, 0)} if generation == 0 else {(0, generation)} | {
            (first, generation - 1 - first) for first in range(1, generation)}
        require(coordinates == expected_shell, 'Simple-root generation formula differs.')
        require(len(shell) == (1 if generation == 0 else generation),
                'Simple-root cardinality mismatch.')
        for first, second in coordinates:
            require(first + second + (1 if first else 0) == generation,
                    'Simple-root distance mismatch.')
        counts.append(len(shell))
        if generation >= 3:
            require(counts[-1] == 2 * counts[-2] - counts[-3],
                    'Simple-root recurrence mismatch.')
    require(counts[3] == 3, 'Corrected Table 5 value differs.')
    return {'depth': depth, 'residues': len(seen), 'initial_counts': counts[:11],
            'shells_equal': True, 'distances_equal': True, 'recurrence_from': 3,
            'corrected_table5_G3': 3}


def hex_shell(generation):
    if generation == 0:
        return {(0, 0)}
    rays = ((1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1))
    expected = set()
    for index, ray in enumerate(rays):
        radius = generation - index
        if radius >= 1:
            expected.add((radius * ray[0], radius * ray[1]))
        offset = min(index + 1, 5)
        total = generation - offset
        following = rays[(index + 1) % 6]
        for first in range(1, total):
            second = total - first
            expected.add((first * ray[0] + second * following[0],
                          first * ray[1] + second * following[1]))
    return expected


def check_hex(depth):
    pair_seen = {(0, 0)}
    pair_shell = {(0, 0)}
    counts = []
    for generation, (shell, seen) in enumerate(polynomial_shells((1, -1, 1), depth)):
        coordinates = {(polynomial[0] if polynomial else 0,
                        polynomial[1] if len(polynomial) > 1 else 0)
                       for polynomial in shell}
        require(coordinates == pair_shell, 'Hexagonal polynomial and pair shells differ.')
        require(coordinates == hex_shell(generation), 'Hexagonal sector distances differ.')
        expected = (1 if generation == 0 else
                    sum(generation >= index + 1 for index in range(6)) +
                    sum(max(generation - index - 1, 0) for index in range(1, 6)) +
                    max(generation - 6, 0))
        require(len(shell) == expected, 'Hexagonal count differs.')
        if generation >= 6:
            require(len(shell) == 6 * generation - 20, 'Hexagonal linear formula differs.')
        counts.append(len(shell))
        numerator = [1, -1, 1, 1, 1, 1, 1, 1]
        difference = counts[-1] - (2 * counts[-2] if generation else 0)
        difference += counts[-3] if generation >= 2 else 0
        require(difference == (numerator[generation] if generation < 8 else 0),
                'Hexagonal generating function differs.')
        candidates = {(constant + 1, linear) for constant, linear in pair_shell}
        candidates.update((-linear, constant + linear) for constant, linear in pair_shell)
        pair_shell = candidates - pair_seen
        pair_seen.update(pair_shell)
    require(counts[:11] == [1, 1, 2, 4, 7, 11, 16, 22, 28, 34, 40],
            'Hexagonal Table 5 values differ.')
    require(counts[7] != 2 * counts[6] - counts[5], 'Hexagonal sharp onset differs.')
    return {'depth': depth, 'residues': len(seen), 'initial_counts': counts[:11],
            'shells_equal': True, 'sector_distances_equal': True,
            'recurrence_from': 8, 'onset_sharp': True, 'linear_formula_from': 6}


def check_cyclic(maximum_degree=6, depth=16):
    results = []
    for degree in range(1, maximum_degree + 1):
        divisor = (-1,) + (0,) * (degree - 1) + (1,)
        counts = []
        for generation, (shell, seen) in enumerate(polynomial_shells(divisor, depth)):
            for polynomial in shell:
                require(all(coefficient >= 0 for coefficient in polynomial),
                        'Cyclic coefficient is negative.')
                distance = sum(polynomial) + len(polynomial) - 1 if polynomial else 0
                require(distance == generation, 'Cyclic distance differs.')
            expected = (1 if generation == 0 else
                        sum(comb(generation - 1, index) for index in range(degree)
                            if index < generation))
            require(len(shell) == expected, 'Cyclic generation count differs.')
            counts.append(len(shell))
        results.append({'degree': degree, 'depth': depth, 'residues': len(seen),
                        'initial_counts': counts[:11], 'distances_equal': True,
                        'counts_equal': True})
    return results


def check_predecessor_equality():
    distances = {}
    for generation, (shell, seen) in enumerate(polynomial_shells((-2, 0, 1), 3)):
        for polynomial in shell:
            distances[polynomial] = generation
    require(distances[(3,)] == distances[(0, 2)] == 3,
            'The square-root-two predecessor equality differs.')
    return {'constant_endpoint': 3, 'radical_coefficient': 2,
            'both_distances': 3, 'depth': 3}


def main():
    parser = argparse.ArgumentParser(description='Exact finite polynomial-tree checks.')
    parser.add_argument('--depth', type=int, default=80)
    arguments = parser.parse_args()
    require(10 <= arguments.depth <= 100, 'Choose a depth between 10 and 100.')
    result = {'schema_version': 1, 'arithmetic': 'exact integers',
              'universal_tree': {'depth': 13, 'polynomials': check_universal(13)},
              'double_root': check_double(arguments.depth),
              'simple_root': check_simple(arguments.depth),
              'hexagonal': check_hex(arguments.depth),
              'cyclic_quotients': check_cyclic(),
              'predecessor_equality': check_predecessor_equality(),
              'scope': 'Finite checks through the stated depths; general statements have written proofs.',
              'status': 'ALL_CHECKS_OK'}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
