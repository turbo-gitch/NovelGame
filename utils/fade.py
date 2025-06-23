import pygame

def fade_in_home(screen, clock, fade_speed=2, draw_callback=None):
    """
    画面をフェードインさせる関数。
    完全に黒から徐々に透明になっていくエフェクト。
    """
    width, height = screen.get_size()
    
    # フェード用の一時的なサーフェスを作成
    temp_screen = pygame.Surface((width, height))
    
    # フェード中のメインループ
    fade_alpha = 255
    while fade_alpha > 0:
        # イベント処理（キューをクリアするだけ）
        pygame.event.clear()
        
        # 背景描画
        if draw_callback:
            draw_callback()
            
        # フェード効果用の黒いオーバーレイを描画
        temp_screen.fill((0, 0, 0))
        temp_screen.set_alpha(fade_alpha)
        screen.blit(temp_screen, (0, 0))
        
        # 画面更新
        pygame.display.flip()  # update()ではなくflip()を使用
        
        # アルファ値を減少
        fade_alpha -= fade_speed
        if fade_alpha < 0:
            fade_alpha = 0
            
        # フレームレート制御
        clock.tick(60)
    
    # フェード完了後、最終的な画面を描画して確実に更新
    if draw_callback:
        draw_callback()
        pygame.display.flip()  # 最終的な画面を確実に更新