from base import SceneBase
import pygame
import sys

def is_button_clicked(button_rect, event):
    """ボタンがクリックされたかどうかを判定する関数"""
    # イベントが無効な場合は早期リターン
    if event.type != pygame.MOUSEBUTTONDOWN:
        return False
        
    # ボタンの矩形内にマウス位置があるかチェック
    return button_rect.collidepoint(event.pos)

def draw_button(screen, text, position, font_size=48, bg_color=(40, 60, 120), text_color=(255, 255, 255), font_path=None):
    """シンプルでかっこいいボタンを描画"""
    if font_path:
        font = pygame.font.Font(font_path, font_size)
    else:
        font = pygame.font.Font(None, font_size)
    font.set_bold(True)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect()

    padding_x, padding_y = 36, 18
    button_rect = pygame.Rect(
        position[0],
        position[1],
        text_rect.width + padding_x * 2,
        text_rect.height + padding_y * 2
    )

    # マウスオーバー判定
    mouse_pos = pygame.mouse.get_pos()
    is_hover = button_rect.collidepoint(mouse_pos)

    # シャドウ
    shadow_rect = button_rect.copy()
    shadow_rect.x += 4
    shadow_rect.y += 4
    shadow_color = (0, 0, 0, 80)
    shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, shadow_color, shadow_surf.get_rect(), border_radius=18)
    screen.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))

    # ボタン本体
    btn_surf = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
    base_color = (bg_color[0], bg_color[1], bg_color[2], 180 if not is_hover else 230)
    pygame.draw.rect(btn_surf, base_color, btn_surf.get_rect(), border_radius=18)
    pygame.draw.rect(btn_surf, (255, 255, 255, 120), btn_surf.get_rect(), 2, border_radius=18)
    screen.blit(btn_surf, (button_rect.x, button_rect.y))

    # テキスト中央
    text_x = button_rect.x + (button_rect.width - text_rect.width) // 2
    text_y = button_rect.y + (button_rect.height - text_rect.height) // 2
    screen.blit(text_surface, (text_x, text_y))

    return button_rect