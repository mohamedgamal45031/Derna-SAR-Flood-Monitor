
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import json
from PIL import Image

st.set_page_config(
    page_title="Derna SAR Flood Monitor",
    page_icon="🛰️",
    layout="wide"
)

st.title("🛰️ Derna SAR Flood Monitor")
st.subheader("NASA Space Apps Challenge | Derna, Libya")

st.markdown("""
نظام رصد ومقارنة صور الأقمار الصناعية باستخدام تقنية
Synthetic Aperture Radar (SAR) لمراقبة المناطق المتأثرة
بالفيضانات في مدينة درنة.
""")

st.info("""
Upload two SAR images: one before the flood and one after.
The system will compare them and generate a change-detection map.
""")

# ==========================================
# UPLOAD IMAGES
# ==========================================

st.sidebar.header("📤 Upload Satellite Images")

before_file = st.sidebar.file_uploader(
    "Before Flood Image",
    type=["png", "jpg", "jpeg", "tif", "tiff"]
)

after_file = st.sidebar.file_uploader(
    "After Flood Image",
    type=["png", "jpg", "jpeg", "tif", "tiff"]
)

# ==========================================
# ANALYSIS SETTINGS
# ==========================================

st.sidebar.markdown("---")

threshold = st.sidebar.slider(
    "After Image Threshold",
    -25.0, 0.0, -16.0, 0.5
)

change_threshold = st.sidebar.slider(
    "Minimum Change Threshold",
    1.0, 15.0, 4.0, 0.5
)

pixel_size = st.sidebar.number_input(
    "Pixel Size (meters)",
    min_value=1,
    max_value=1000,
    value=10
)

# ==========================================
# IMAGE LOADING
# ==========================================

def load_image(uploaded_file):

    image = Image.open(uploaded_file).convert("L")

    return np.array(image, dtype=np.float32)


# ==========================================
# SIMULATED DEMO DATA
# ==========================================

def generate_demo():

    np.random.seed(42)

    before = np.random.normal(-9.5, 1.2, (300, 300))

    after = before.copy()

    after[100:220, 120:180] = np.random.normal(
        -19.8, 0.8, (120, 60)
    )

    after[150:190, 180:210] = np.random.normal(
        -17.5, 1.0, (40, 30)
    )

    return before, after


# ==========================================
# MAIN APPLICATION
# ==========================================

if before_file is not None and after_file is not None:

    try:

        before = load_image(before_file)
        after = load_image(after_file)

        if before.shape != after.shape:

            st.warning(
                "Image dimensions differ. Resizing the After image."
            )

            resized = Image.fromarray(
                np.uint8(np.clip(after, 0, 255))
            ).resize((before.shape[1], before.shape[0]))

            after = np.array(resized, dtype=np.float32)

        # IMPORTANT:
        # Grayscale images are not calibrated SAR backscatter.
        # This analysis is visual change detection only.
        difference = before - after

        st.success("Both images uploaded successfully!")

        st.header("🛰️ Satellite Image Comparison")

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("Before Flood")

            fig, ax = plt.subplots(figsize=(7, 5))
            ax.imshow(before, cmap="gray")
            ax.axis("off")
            st.pyplot(fig)
            plt.close(fig)

        with col2:

            st.subheader("After Flood")

            fig, ax = plt.subplots(figsize=(7, 5))
            ax.imshow(after, cmap="gray")
            ax.axis("off")
            st.pyplot(fig)
            plt.close(fig)

        # Change detection
        # For calibrated SAR in dB, lower after-backscatter
        # and a positive before-after difference can indicate
        # possible open-water flooding.
        mask = (
            (after < threshold) &
            (difference > change_threshold)
        )

        affected_pixels = int(np.sum(mask))
        total_pixels = before.size

        area = (
            affected_pixels * pixel_size * pixel_size
        ) / 1_000_000

        percentage = affected_pixels / total_pixels * 100

        st.markdown("---")
        st.header("📊 Flood Analysis")

        c1, c2, c3 = st.columns(3)

        c1.metric("Affected Area", f"{area:.4f} km²")
        c2.metric("Affected Pixels", f"{affected_pixels:,}")
        c3.metric("Changed Area", f"{percentage:.2f}%")

        # Flood map

        st.header("🗺️ Change Detection Map")

        fig, ax = plt.subplots(figsize=(9, 6))

        ax.imshow(mask, cmap="Reds")
        ax.set_title("Potential Flood-Affected Pixels")
        ax.axis("off")

        st.pyplot(fig)
        plt.close(fig)

        # Difference map

        st.header("📉 Image Difference")

        fig, ax = plt.subplots(figsize=(9, 6))

        image = ax.imshow(
            difference,
            cmap="RdYlBu_r"
        )

        plt.colorbar(image, ax=ax)
        ax.axis("off")

        st.pyplot(fig)
        plt.close(fig)

        # Report

        report = {
            "Project": "Derna SAR Flood Monitor",
            "Location": "Derna, Libya",
            "Before_Image": before_file.name,
            "After_Image": after_file.name,
            "Image_Type": "Uploaded grayscale imagery",
            "Pixel_Size_Meters": pixel_size,
            "Affected_Pixels": affected_pixels,
            "Affected_Area_SqKm": round(area, 4),
            "Changed_Percentage": round(percentage, 2),
            "Scientific_Validation": "Requires calibrated and co-registered SAR data"
        }

        st.header("📄 Flood Report")

        st.json(report)

        st.download_button(
            "⬇️ Download JSON Report",
            data=json.dumps(report, indent=4),
            file_name="derna_flood_report.json",
            mime="application/json"
        )

    except Exception as e:

        st.error(f"Image processing error: {e}")

elif before_file is None and after_file is None:

    st.header("🌊 Flood Monitoring Preview")

    st.write(
        "Upload your Before and After images using the sidebar "
        "to start the analysis."
    )

    st.info(
        "You can upload PNG, JPG, or TIFF images."
    )

elif before_file is None:

    st.warning("Please upload the Before Flood image.")

else:

    st.warning("Please upload the After Flood image.")

# ==========================================
# FOOTER
# ==========================================

st.markdown("---")

st.caption("""
NASA Space Apps Challenge | Derna Flood Monitoring

Note: Accurate flood-area estimation requires calibrated
Sentinel-1 SAR data, image co-registration, appropriate
backscatter processing, and geographic pixel-area information.
""")
