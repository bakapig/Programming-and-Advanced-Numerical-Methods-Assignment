% Inputs:
%   fwd: forward spot for time T, i.e. E[S(T)]
%   T: time to expiry of the option
%   cp: 1 for call, -1 for put (can be vector)
%   sigma: implied Black volatility of the option (can be vector)
%   delta: delta in absolute value (e.g. 0.25) (can be vector)
% Output:
%   K: strike of the option
function K = getStrikeFromDelta(fwd, T, cp, sigma, delta)

    if ~(isscalar(fwd) && isnumeric(fwd) && isreal(fwd) && isfinite(fwd) && fwd > 0)
        error('getStrikeFromDelta:InvalidForward. fwd must be a finite strictly positive real scalar.');
    end
    if ~(isscalar(T) && isnumeric(T) && isreal(T) && isfinite(T) && T > 0)
        error('getStrikeFromDelta:InvalidMaturity. T must be a finite strictly positive real scalar.');
    end
    if ~(isnumeric(cp) && isreal(cp) && isnumeric(sigma) && isreal(sigma) && isnumeric(delta) && isreal(delta))
        error('getStrikeFromDelta:InvalidInput. cp, sigma and delta must be real numeric arrays or scalars.');
    end

    % 1. Inverse Normal of the Delta (using erfinv to avoid toolboxes)
    % N_inv(delta) = sqrt(2) * erfinv(2 * delta - 1)
    norm_inv_delta = sqrt(2) .* erfinv(2 .* delta - 1);
    
    % 2. Find the required d1 value
    % Since Delta = N(cp * d1), then d1 = cp * N_inv(delta)
    d1 = cp .* norm_inv_delta;
    
    % 3. Algebraically solve the d1 formula for K
    % This completely avoids the need for a slow, error-prone fzero search!
    exponent = -sigma .* sqrt(T) .* (d1 - 0.5 .* sigma .* sqrt(T));
    K = fwd .* exp(exponent);

end