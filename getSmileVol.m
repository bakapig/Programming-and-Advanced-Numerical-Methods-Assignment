% Inputs :
% curve : pre - computed smile data
% Ks: vetor of strikes
% Output :
% vols : implied volatility at strikes Ks
function vols = getSmileVol(curve, Ks)

    if ~(isstruct(curve) && isfield(curve, 'pp') && isfield(curve, 'aL') && ...
            isfield(curve, 'bL') && isfield(curve, 'aR') && isfield(curve, 'bR'))
        error('getSmileVol:InvalidCurve. curve must be a struct created by makeSmile.');
    end
    if ~(isnumeric(Ks) && isreal(Ks) && ~isempty(Ks))
        error('getSmileVol:InvalidStrikes. Ks must be a non-empty real numeric array.');
    end
    if any(~isfinite(Ks(:))) || any(Ks(:) < 0)
        error('getSmileVol:InvalidStrikes. Ks must contain only finite non-negative strikes.');
    end

    % Pre-allocate the output array for maximum speed
    vols = zeros(size(Ks));
    
    % Extract boundary strikes and volatilities from our pre-computed curve
    K1 = curve.Ks(1);
    KN = curve.Ks(end);
    vol_K1 = curve.vols(1);
    vol_KN = curve.vols(end);
    
    % 1. Left Wing Extrapolation (Ks < K1)
    % Formula: spline(K1) + aL * tanh(bL * (K1 - Ks))
    idx_L = Ks < K1;
    vols(idx_L) = vol_K1 + curve.aL .* tanh(curve.bL .* (K1 - Ks(idx_L)));
    
    % 2. Right Wing Extrapolation (Ks > KN)
    % Formula: spline(KN) + aR * tanh(bR * (Ks - KN))
    idx_R = Ks > KN;
    vols(idx_R) = vol_KN + curve.aR .* tanh(curve.bR .* (Ks(idx_R) - KN));
    
    % 3. Inner Interval Interpolation (K1 <= Ks <= KN)
    % Formula: Evaluate the cubic spline
    idx_mid = ~idx_L & ~idx_R;
    if any(idx_mid)
        vols(idx_mid) = ppval(curve.pp, Ks(idx_mid));
    end

end