def draw_background(p, logo_path, width, height):
    if os.path.exists(logo_path):
        try:
            p.saveState()
            p.drawImage(
                ImageReader(logo_path),
                0, 0,
                width=width,
                height=height,
                preserveAspectRatio=True,
                mask='auto'
            )
            p.restoreState()
        except Exception as e:
            print(f"Failed to draw background image: {e}")