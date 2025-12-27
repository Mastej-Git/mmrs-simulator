import numpy as np
from dataclasses import dataclass


@dataclass
class Sector:
    t_l: float
    t_u: float
    addresses: list[list]


class CollisionSectorAlgorithm:

    def get_bezier_data(self, t: np.ndarray, verts: np.ndarray):
        t = t[:, np.newaxis]
        p0, p1, p2 = verts
        pts = (1 - t)**2 * p0 + 2 * (1 - t) * t * p1 + t**2 * p2
        vel = 2 * (1 - t) * (p1 - p0) + 2 * t * (p2 - p1)
        return pts, vel

    def find_precise_root(self, fixed_pt: np.ndarray, verts_other: np.ndarray, R_sq: float, t_guess: float):
        """Newton-Raphson to find where ||P(t) - fixed_pt||^2 = R^2."""
        t = t_guess
        for _ in range(5):
            p, v = self.get_bezier_data(np.array([t]), verts_other)
            p, v = p[0], v[0]
            diff = p - fixed_pt
            f = np.dot(diff, diff) - R_sq
            df = 2 * np.dot(diff, v)
            if abs(df) < 1e-10: break
            
            t_new = np.clip(t - f/df, 0, 1)
            if abs(t_new - t) < 1e-7: return t_new
            t = t_new
        return t

    def process_curve_pair_fast(self, verts1_list, verts2_list, r1, r2, ef=1.1):
        v1, v2 = np.array(verts1_list), np.array(verts2_list)
        R = (r1 + r2) * ef
        R_sq = R**2
        
        # 1. Broad Phase: AABB overlap check
        margin = R
        aabb1 = np.concatenate([np.min(v1, 0) - margin, np.max(v1, 0) + margin])
        aabb2 = np.concatenate([np.min(v2, 0), np.max(v2, 0)])
        if (aabb1[2] < aabb2[0] or aabb1[0] > aabb2[2] or 
            aabb1[3] < aabb2[1] or aabb1[1] > aabb2[3]):
            return None

        # 2. Narrow Phase: Vectorized check
        t_samples = np.linspace(0, 1, 12)
        pts1, _ = self.get_bezier_data(t_samples, v1)
        pts2, _ = self.get_bezier_data(t_samples, v2)
        
        # Distances between all sample points
        diffs = pts1[:, np.newaxis, :] - pts2[np.newaxis, :, :]
        dists_sq = np.sum(diffs**2, axis=2)
        
        # 3. Expansion
        mask = dists_sq < R_sq
        if not np.any(mask): return None
        
        # Find the parameter ranges that violate the distance
        hit_indices = np.argwhere(mask)
        t_hits = t_samples[hit_indices[:, 0]]
        v_hits = t_samples[hit_indices[:, 1]]
        
        # Boundary Refinement: Find exactly where distance becomes R
        # We take the min/max hit as starting points for Newton
        t_min, t_max = np.min(t_hits), np.max(t_hits)
        v_min, v_max = np.min(v_hits), np.max(v_hits)
        
        # Refine boundaries on Curve 1
        t_l = self.find_precise_root(pts2[hit_indices[0,1]], v1, R_sq, t_min)
        t_u = self.find_precise_root(pts2[hit_indices[-1,1]], v1, R_sq, t_max)
        
        # Refine boundaries on Curve 2
        v_l = self.find_precise_root(pts1[hit_indices[0,0]], v2, R_sq, v_min)
        v_u = self.find_precise_root(pts1[hit_indices[-1,0]], v2, R_sq, v_max)

        # pair_id = f"{verts1_list}, {verts2_list}"
        pair_id = [verts1_list, verts2_list]
        return (Sector(t_l, t_u, pair_id), Sector(v_l, v_u, pair_id))

