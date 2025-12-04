from hub import light_matrix, sound
import runloop

async def main():
    # Star Wars Imperial March Theme
    # Play the iconic "Dun Dun Dun" opening
    
    # Main theme notes (simplified version)
    # Using different waveforms and frequencies for variety
    
    # Opening dramatic notes - G (392 Hz)
    await sound.beep(392, 500, 100)
    await runloop.sleep_ms(100)
    await sound.beep(392, 500, 100)
    await runloop.sleep_ms(100)
    await sound.beep(392, 500, 100)
    await runloop.sleep_ms(100)
    
    # Lower dramatic note - Eb (311 Hz)
    await sound.beep(311, 400, 100)
    await runloop.sleep_ms(50)
    
    # Higher note - Bb (466 Hz)
    await sound.beep(466, 200, 80)
    await runloop.sleep_ms(50)
    
    # Back to main theme
    await sound.beep(392, 500, 100)
    await runloop.sleep_ms(100)
    await sound.beep(311, 400, 100)
    await runloop.sleep_ms(50)
    await sound.beep(466, 200, 80)
    await runloop.sleep_ms(50)
    await sound.beep(392, 800, 100)
    await runloop.sleep_ms(200)
    
    # Second phrase - D (587 Hz)
    await sound.beep(587, 500, 90)
    await runloop.sleep_ms(100)
    await sound.beep(587, 500, 90)
    await runloop.sleep_ms(100)
    await sound.beep(587, 500, 90)
    await runloop.sleep_ms(100)
    
    # Eb (622 Hz)
    await sound.beep(622, 400, 90)
    await runloop.sleep_ms(50)
    await sound.beep(466, 200, 80)
    await runloop.sleep_ms(50)
    
    # Final dramatic sequence - F# (370 Hz)
    await sound.beep(370, 500, 100)
    await runloop.sleep_ms(100)
    await sound.beep(311, 400, 100)
    await runloop.sleep_ms(50)
    await sound.beep(466, 200, 80)
    await runloop.sleep_ms(50)
    await sound.beep(392, 1000, 100)  # Final G
    
    # Add some light effects to enhance the Star Wars feel
    light_matrix.show_image(light_matrix.IMAGE_HAPPY)
    await runloop.sleep_ms(500)
    light_matrix.show_image(light_matrix.IMAGE_HEART)
    await runloop.sleep_ms(500)
    light_matrix.clear()

runloop.run(main())