import operator

def get_operator_fn(op):
    return {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '//': operator.floordiv,
        '%': operator.mod,
        '^': operator.xor,
        '==': operator.eq,
        '>': operator.gt,
        '>=': operator.ge,
        '<': operator.lt,
        '<=': operator.le
    }[op]


def eval_binary_expr(op1, optr, op2):
    return get_operator_fn(optr)(op1, op2)

