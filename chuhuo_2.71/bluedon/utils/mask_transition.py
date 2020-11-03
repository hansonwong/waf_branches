#! /usr/bin/env python
# -*- coding:utf-8 -*-


# def exchange_mask(mask):
#     """
#     转换子网掩码格式
#     """
#     count_bit = lambda bin_str: len([i for i in bin_str if i=='1'])
#     mask_splited = mask.split('.')
#     mask_count = [count_bit(bin(int(i))) for i in mask_splited]
#     return sum(mask_count)

def exchange_mask(mask):
    """
    转换子网掩码格式
    >>> exchange_mask('255.255.255.255')
    32
    >>> exchange_mask('255.255.255.0')
    24
    """

    if '.' not in mask: return mask
    mask_bin = ''.join([bin(int(i)) for i in mask.split('.')])
    return mask_bin.count('1')


def strmask_to_intv6(mask):
    if ':' not in mask: return mask
    mask_bin = ''.join([bin(int(i, 16)) for i in mask.split(':') if i])
    return mask_bin.count('1')


def int_to_strmask(num):
    """
    eg: '24' --> '255.255.255.0'
    args:
        mask: mask digit
    return:
        change mask
    """
    if '.' in num:
        return num
    num = int(num)
    bin_str = '{:0<32}'.format('1'*num)
    bin_str = [str(int(bin_str[i:i+8], 2)) for i in range(0, 32, 8)]
    return '.'.join(bin_str)


def ex_mask(mask):
    """
    args:
        mask: '24' or '255.255.255.0'
    returns:
        mask1: int
        mask2: str
    """
    mask1 = exchange_mask(mask)
    mask2 = int_to_strmask(mask)
    return mask1, mask2


if __name__ == '__main__':
    #import doctest
    #doctest.testmod()
    mask=exchange_mask('255.255.255.0')
