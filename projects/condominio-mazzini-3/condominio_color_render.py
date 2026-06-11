#!/usr/bin/env python3
"""
Condominio Mazzini — Color Rendering v2
Usa K-means per identificare i colori reali della facciata in ogni foto.
Applica i 3 colori della palette: dominante, secondario, accessori.
Corregge anche la luminosità per colori chiari/scuri.
"""
import cv2
import numpy as np
import json
import os
import sys

ORIG_DIR = "/home/openclaw/attibot/condominio/img/originali"
OUT_DIR  = "/home/openclaw/attibot/condominio/img"
JSON_FILE = "/home/openclaw/attibot/condominio/TODO_RENDERING.json"
PHOTOS = ["foto1.jpg", "foto2.jpg", "foto3.jpg"]

def hex_to_lab(hex_color):
    h = hex_color.lstrip('#')
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    bgr = np.array([[[b, g, r]]], dtype=np.uint8)
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)[0][0].astype(np.float32)

def create_masks_kmeans(img, n_clusters=10):
    """K-means adattivo: trova i cluster di colore reali della foto."""
    h, w = img.shape[:2]
    pixels = img.reshape(-1, 3).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 40, 0.05)
    _, labels, centers = cv2.kmeans(pixels, n_clusters, None, criteria, 5, cv2.KMEANS_PP_CENTERS)
    labels_img = labels.reshape(h, w)

    # Converti centri in HSV per classificarli
    centers_uint8 = centers.astype(np.uint8).reshape(1, -1, 3)
    hsv_centers = cv2.cvtColor(centers_uint8, cv2.COLOR_BGR2HSV)[0]

    facade_ids, cream_ids, concrete_ids = [], [], []

    for i, (bgr, hsv_c) in enumerate(zip(centers, hsv_centers)):
        hue, sat, val = float(hsv_c[0]), float(hsv_c[1]), float(hsv_c[2])
        count = int(np.sum(labels == i))

        # ROSSO/SALMONE (facciata principale): hue 0-20 o 160-180, sat>50, val>40
        if (hue < 22 or hue > 158) and sat > 50 and val > 40:
            facade_ids.append((count, i))

        # CREMA/BEIGE (fasce orizzontali, soffitti balconi): hue 10-50, sat<90, val>120
        elif 8 < hue < 55 and sat < 90 and val > 120:
            cream_ids.append((count, i))

        # GRIGIO/CEMENTO (contorni finestre, elementi strutturali): bassa sat, val media
        elif sat < 45 and 60 < val < 200:
            concrete_ids.append((count, i))

    def build_mask(cluster_ids, max_clusters=3):
        mask = np.zeros((h, w), dtype=np.uint8)
        for _, cid in sorted(cluster_ids, reverse=True)[:max_clusters]:
            mask[labels_img == cid] = 255
        return mask

    mask_dom = build_mask(facade_ids, max_clusters=4)
    mask_sec = build_mask(cream_ids, max_clusters=3)
    mask_acc = build_mask(concrete_ids, max_clusters=2)

    # Maschera di esclusione: cielo + vegetazione + terra
    hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    sky_mask = cv2.inRange(hsv_img, np.array([95,  15, 140]), np.array([145, 255, 255]))  # azzurro/blu
    veg_mask = cv2.inRange(hsv_img, np.array([32,  35,  25]), np.array([92,  255, 255]))  # verde erba/alberi
    # escludi anche la fascia inferiore (terreno/marciapiede, ~20% bottom)
    ground_mask = np.zeros((h, w), dtype=np.uint8)
    ground_mask[int(h * 0.82):, :] = 255
    exclude = cv2.bitwise_or(sky_mask, veg_mask)
    exclude = cv2.bitwise_or(exclude, ground_mask)

    # Pulizia morfologica
    k5, k3 = np.ones((5,5), np.uint8), np.ones((3,3), np.uint8)

    mask_dom = cv2.morphologyEx(mask_dom, cv2.MORPH_CLOSE, k5)
    mask_dom = cv2.morphologyEx(mask_dom, cv2.MORPH_OPEN,  k3)
    mask_dom = cv2.dilate(mask_dom, k3, iterations=2)

    mask_sec = cv2.morphologyEx(mask_sec, cv2.MORPH_CLOSE, k5)
    mask_sec = cv2.morphologyEx(mask_sec, cv2.MORPH_OPEN,  k3)

    # applica esclusione
    mask_dom = cv2.bitwise_and(mask_dom, cv2.bitwise_not(exclude))
    mask_sec = cv2.bitwise_and(mask_sec, cv2.bitwise_not(exclude))
    mask_acc = cv2.bitwise_and(mask_acc, cv2.bitwise_not(exclude))

    # evita sovrapposizioni
    mask_sec = cv2.bitwise_and(mask_sec, cv2.bitwise_not(mask_dom))
    mask_acc = cv2.bitwise_and(mask_acc, cv2.bitwise_not(mask_dom))
    mask_acc = cv2.bitwise_and(mask_acc, cv2.bitwise_not(mask_sec))

    return mask_dom, mask_sec, mask_acc

def apply_color_lab(img, mask, target_hex, color_strength=0.82, lum_strength=0.55):
    """LAB color transfer con correzione luminosità verso il colore target."""
    if not np.any(mask > 0):
        return img
    t = hex_to_lab(target_hex)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    result = lab.copy()
    m = mask > 0

    # Sostituisci A e B (crominanza = colore)
    result[m, 1] = t[1] * color_strength + result[m, 1] * (1 - color_strength)
    result[m, 2] = t[2] * color_strength + result[m, 2] * (1 - color_strength)

    # Correggi luminosità verso il target (evita bianchi grigi e neri marroni)
    target_L = float(t[0])
    current_L_mean = float(np.mean(lab[m, 0]))
    if abs(target_L - current_L_mean) > 25:  # differenza significativa
        result[m, 0] = result[m, 0] * (1 - lum_strength) + target_L * lum_strength

    result = np.clip(result, 0, 255).astype(np.uint8)
    out = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)

    # Sfuma i bordi
    blur = cv2.GaussianBlur(mask.astype(np.float32)/255.0, (19,19), 0)[:,:,np.newaxis]
    final = out.astype(np.float32)*blur + img.astype(np.float32)*(1-blur)
    return np.clip(final, 0, 255).astype(np.uint8)

def process_proposal(proposal, verbose=False):
    code    = proposal['code']
    dom_hex = proposal['dominant']['hex']
    sec_hex = proposal['secondary']['hex']
    acc_hex = proposal.get('accessory', {}).get('hex', '')
    results = []

    for i, photo in enumerate(PHOTOS, 1):
        src = os.path.join(ORIG_DIR, photo)
        dst = os.path.join(OUT_DIR, f"{code}_foto{i}.jpg")
        img = cv2.imread(src)
        if img is None:
            print(f"  SKIP {src}")
            continue

        mask_dom, mask_sec, mask_acc = create_masks_kmeans(img)

        result = apply_color_lab(img,    mask_dom, dom_hex)
        result = apply_color_lab(result, mask_sec, sec_hex)
        if acc_hex:
            result = apply_color_lab(result, mask_acc, acc_hex, color_strength=0.6, lum_strength=0.35)

        cv2.imwrite(dst, result, [cv2.IMWRITE_JPEG_QUALITY, 93])
        if verbose:
            dom_pct = int(np.sum(mask_dom > 0) / (img.shape[0]*img.shape[1]) * 100)
            sec_pct = int(np.sum(mask_sec > 0) / (img.shape[0]*img.shape[1]) * 100)
            acc_pct = int(np.sum(mask_acc > 0) / (img.shape[0]*img.shape[1]) * 100)
            print(f"  OK  {dst}  (dom {dom_pct}% sec {sec_pct}% acc {acc_pct}%)")
        else:
            print(f"  OK  {dst}")
        results.append(f"img/{code}_foto{i}.jpg")
    return results

def update_json(code, renderings):
    with open(JSON_FILE) as f:
        data = json.load(f)
    for p in data['proposals']:
        if p['code'] == code:
            p['status'] = 'done'
            p['renderings'] = {f"foto{j+1}": r for j, r in enumerate(renderings)}
    data['completed'] = sum(1 for p in data['proposals'] if p['status'] == 'done')
    with open(JSON_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    codes = sys.argv[1:] if len(sys.argv) > 1 else None
    verbose = '--verbose' in (codes or [])
    if verbose:
        codes = [c for c in codes if c != '--verbose']

    with open(JSON_FILE) as f:
        data = json.load(f)

    for p in data['proposals']:
        if codes and p['code'] not in codes:
            continue
        if not codes and p['status'] == 'done':
            continue
        print(f"\n→ {p['code']} — {p['title']}")
        renderings = process_proposal(p, verbose=verbose)
        if renderings:
            update_json(p['code'], renderings)
    print("\nDone.")

if __name__ == '__main__':
    main()
