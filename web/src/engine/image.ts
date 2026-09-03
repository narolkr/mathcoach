/**
 * Turning a phone photo into something worth sending.
 *
 * A modern phone camera produces 3-12 MB and 4000+ pixels on the long edge.
 * Sending that raw would be slow on mobile data, burn tokens for no benefit,
 * and on a tight free-tier quota that matters. Downscaling to ~1568px is the
 * point where handwriting is still comfortably legible.
 */

/** Long edge, in pixels. Beyond this, handwriting legibility stops improving. */
const MAX_EDGE = 1568;
const JPEG_QUALITY = 0.85;

export interface PreparedImage {
  /** Base64 with no data: prefix, which is what the API wants. */
  base64: string;
  mimeType: "image/jpeg";
  width: number;
  height: number;
  bytes: number;
  /** A data: URL for showing the thumbnail back to the learner. */
  previewUrl: string;
}

export async function prepareImage(file: File): Promise<PreparedImage> {
  if (!file.type.startsWith("image/")) {
    throw new Error(`That's a ${file.type || "unknown"} file, not an image.`);
  }

  const bitmap = await loadBitmap(file);
  const scale = Math.min(1, MAX_EDGE / Math.max(bitmap.width, bitmap.height));
  const width = Math.max(1, Math.round(bitmap.width * scale));
  const height = Math.max(1, Math.round(bitmap.height * scale));

  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const context = canvas.getContext("2d");
  if (!context) throw new Error("This browser wouldn't give us a canvas to resize with.");

  // White behind the photo: pencil on paper photographed in poor light can
  // carry an alpha channel from some pipelines, and JPEG has no alpha - the
  // default would composite to black and hide the writing.
  context.fillStyle = "#ffffff";
  context.fillRect(0, 0, width, height);
  context.drawImage(bitmap, 0, 0, width, height);
  if ("close" in bitmap) bitmap.close();

  const previewUrl = canvas.toDataURL("image/jpeg", JPEG_QUALITY);
  const base64 = previewUrl.slice(previewUrl.indexOf(",") + 1);

  // iOS Safari returns a blank canvas - and `toDataURL` returns the bare
  // string "data:," - when a decode exceeds its memory limit, which a 48MP
  // photo can. Without this the app would POST an empty image and surface
  // whatever Gemini says about it, which is never the actual cause.
  if (base64.length < 512) {
    throw new Error(
      "The browser couldn't encode that photo - it may be too large for " +
        "this device to process. Try a photo taken at a lower resolution.",
    );
  }

  return {
    base64,
    mimeType: "image/jpeg",
    width,
    height,
    // Base64 carries 3 bytes in every 4 characters.
    bytes: Math.round((base64.length * 3) / 4),
    previewUrl,
  };
}

async function loadBitmap(file: File): Promise<ImageBitmap | HTMLImageElement> {
  if ("createImageBitmap" in window) {
    try {
      // Honours the EXIF orientation tag, so a photo taken in portrait is not
      // analysed sideways - which would defeat the whole feature.
      return await createImageBitmap(file, { imageOrientation: "from-image" });
    } catch {
      // Fall through to the <img> path.
    }
  }

  const url = URL.createObjectURL(file);
  try {
    const image = new Image();
    image.src = url;
    await image.decode();
    return image;
  } finally {
    URL.revokeObjectURL(url);
  }
}
