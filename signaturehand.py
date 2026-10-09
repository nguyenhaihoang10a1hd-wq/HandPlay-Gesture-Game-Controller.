import math
from pynput.keyboard import Controller


keyboard = Controller()


def dist(hand, i, j):
    return math.hypot(hand[i].x - hand[j].x, hand[i].y - hand[j].y)

def fingers_curled(hand):
    """4 ngón (trỏ, giữa, áp út, út) co lại: đầu ngón thấp hơn khớp PIP."""
    return all(hand[tip].y > hand[pip].y
               for tip, pip in [(8, 6), (12, 10), (16, 14), (20, 18)])

def is_thumbs_up(hand):
    """Ngón cái chỉ lên trời, 4 ngón còn lại co lại -> phím W."""
    thumb_up = hand[4].y < hand[3].y < hand[2].y < hand[0].y
    thumb_highest = hand[4].y < min(hand[i].y for i in range(5, 21))
    return thumb_up and thumb_highest and fingers_curled(hand)


def fist_any_direction(hand):
    """Nắm tay, không phụ thuộc hướng bàn tay:
    đầu 4 ngón nằm gần cổ tay, không vượt xa gốc ngón (MCP)."""
    return all(dist(hand, tip, 0) < dist(hand, mcp, 0) * 1.2
               for tip, mcp in [(8, 5), (12, 9), (16, 13), (20, 17)])

def thumb_side(hand):
    """Nắm tay, ngón cái duỗi ngang sang bên.
    Trả về "right" (-> D), "left" (-> A) hoặc None."""
    if not fist_any_direction(hand):
        return None

    hand_size = dist(hand, 0, 9)
    dx = hand[4].x - hand[2].x
    dy = hand[4].y - hand[2].y

    thumb_extended = dist(hand, 4, 5) > 0.6 * hand_size
    thumb_horizontal = abs(dx) > 1.5 * abs(dy)
    if not (thumb_extended and thumb_horizontal):
        return None

    return "right" if dx > 0 else "left"


def L_sign(hand):
    """Ký hiệu chữ L: ngón trỏ chỉ lên, ngón cái duỗi ngang,
    3 ngón giữa / áp út / út co lại.
    Trả về "right" (-> W + D), "left" (-> W + A) hoặc None."""
    index_up = hand[8].y < hand[7].y < hand[6].y < hand[5].y

    others_curled = all(dist(hand, tip, 0) < dist(hand, mcp, 0) * 1.2
                        for tip, mcp in [(12, 9), (16, 13), (20, 17)])

    hand_size = dist(hand, 0, 9)
    dx = hand[4].x - hand[2].x
    dy = hand[4].y - hand[2].y
    thumb_out = dist(hand, 4, 5) > 0.6 * hand_size and abs(dx) > 1.2 * abs(dy)

    if not (index_up and others_curled and thumb_out):
        return None
    return "right" if dx > 0 else "left"

def is_point_up(hand):
    """Ngón trỏ chỉ lên, 3 ngón giữa / áp út / út co lại,
    ngón cái gập vào (không duỗi ra).
    Tay trái -> giữ S, tay phải -> bấm liên tục J."""
    index_up = hand[8].y < hand[7].y < hand[6].y < hand[5].y

    others_curled = all(dist(hand, tip, 0) < dist(hand, mcp, 0) * 1.2
                        for tip, mcp in [(12, 9), (16, 13), (20, 17)])

    hand_size = dist(hand, 0, 9)
    thumb_tucked = dist(hand, 4, 5) < 0.7 * hand_size

    return index_up and others_curled and thumb_tucked

def detect_gesture(hand,side):
    """Trả về tên cử chỉ của bàn tay (hoặc None)."""
    L = L_sign(hand)
    if L == "right":
        return "kd"
    if L == "left":
        return "ka"
    if is_thumbs_up(hand):
        return "w" if side == "Left" else "l"
    c = thumb_side(hand)
    if c == "right":
        return "d"
    if c == "left":
        return "a"
    if is_point_up(hand):
        return "s" if side == "Left" else "u"
    return None

def update_held_keys(desired, held):
    """Nhấn giữ các phím mới cần, nhả các phím không còn cần. Trả về tập đang giữ."""

    for k in desired - held:
        keyboard.press(k)
    for k in held - desired:
        keyboard.release(k)
    return set(desired)





