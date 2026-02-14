from hub import light_matrix, sound
import runloop

async def main():
    # Super Mario Bros. Main Theme
    # Play the iconic overworld theme melody
    
    # Note frequencies for Mario theme
    # E5=659, C5=523, G4=392, G5=784, A5=880, F5=698, D5=587, B4=494
    
    # Opening sequence: E - E - _ - E - _ - C - E - _ - G
    await sound.beep(659, 150, 100)  # E
    await runloop.sleep_ms(50)
    await sound.beep(659, 150, 100)  # E
    await runloop.sleep_ms(150)
    await sound.beep(659, 150, 100)  # E
    await runloop.sleep_ms(150)
    await sound.beep(523, 150, 100)  # C
    await runloop.sleep_ms(50)
    await sound.beep(659, 150, 100)  # E
    await runloop.sleep_ms(150)
    await sound.beep(784, 200, 100)  # G
    await runloop.sleep_ms(400)
    await sound.beep(392, 200, 100)  # G (lower octave)
    await runloop.sleep_ms(400)
    
    # Second phrase: C - _ - G - _ - E - _ - A - _ - B - _ - A# - A
    await sound.beep(523, 200, 100)  # C
    await runloop.sleep_ms(200)
    await sound.beep(392, 200, 100)  # G
    await runloop.sleep_ms(200)
    await sound.beep(330, 200, 100)  # E
    await runloop.sleep_ms(200)
    await sound.beep(440, 150, 100)  # A
    await runloop.sleep_ms(50)
    await sound.beep(494, 150, 100)  # B
    await runloop.sleep_ms(50)
    await sound.beep(466, 150, 100)  # A#
    await runloop.sleep_ms(50)
    await sound.beep(440, 200, 100)  # A
    await runloop.sleep_ms(100)
    
    # Third phrase: G - E - G - A - _ - F - G - _ - E - _ - C - D - B
    await sound.beep(392, 100, 100)  # G
    await runloop.sleep_ms(50)
    await sound.beep(659, 100, 100)  # E
    await runloop.sleep_ms(50)
    await sound.beep(784, 100, 100)  # G
    await runloop.sleep_ms(50)
    await sound.beep(880, 150, 100)  # A
    await runloop.sleep_ms(50)
    await sound.beep(698, 150, 100)  # F
    await runloop.sleep_ms(50)
    await sound.beep(784, 150, 100)  # G
    await runloop.sleep_ms(100)
    await sound.beep(659, 150, 100)  # E
    await runloop.sleep_ms(100)
    await sound.beep(523, 150, 100)  # C
    await runloop.sleep_ms(50)
    await sound.beep(587, 150, 100)  # D
    await runloop.sleep_ms(50)
    await sound.beep(494, 300, 100)  # B
    await runloop.sleep_ms(200)
    
    # Add Mario-themed light effects
    # Show happy face like Mario's smile
    light_matrix.show_image(light_matrix.IMAGE_HAPPY)
    await runloop.sleep_ms(500)
    # Show heart like collecting a power-up
    light_matrix.show_image(light_matrix.IMAGE_HEART)
    await runloop.sleep_ms(500)
    # Show arrow up like jumping
    light_matrix.show_image(light_matrix.IMAGE_ARROW_N)
    await runloop.sleep_ms(500)
    light_matrix.clear()

runloop.run(main())