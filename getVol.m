% Inputs:
%   volSurf: volatility surface data (from makeVolSurface)
%   T: time to expiry of the option (scalar or vector)
%   Ks: vector of strikes
% Output:
%   vols: vector of volatilities
%   fwd: forward spot price for maturity T
function [vols, fwd] = getVol(volSurf, T, Ks)

    if ~(isstruct(volSurf) && isfield(volSurf, 'Ts') && isfield(volSurf, 'smiles') && ...
            isfield(volSurf, 'fwds') && isfield(volSurf, 'fwdCurve'))
        error('getVol:InvalidSurface. volSurf must be a struct created by makeVolSurface.');
    end
    if ~(isscalar(T) && isnumeric(T) && isreal(T) && isfinite(T) && T >= 0)
        error('getVol:InvalidMaturity. T must be a finite non-negative real scalar.');
    end
    if ~(isnumeric(Ks) && isreal(Ks) && ~isempty(Ks))
        error('getVol:InvalidStrikes. Ks must be a non-empty real numeric array.');
    end
    if any(~isfinite(Ks(:))) || any(Ks(:) < 0)
        error('getVol:InvalidStrikes. Ks must contain only finite non-negative strikes.');
    end

    Ts = volSurf.Ts(:);
    if T > Ts(end) + 10 * eps(max(1, Ts(end)))
        error('getVol:ExtrapolationNotAllowed. T exceeds the maximum tenor in the volatility surface.');
    end

    % 1. Get the target forward price
    fwd = getFwdSpot(volSurf.fwdCurve, T);
    
    % Ensure T doesn't exceed our maximum data
    if any(T > volSurf.Ts(end))
        error('Time T exceeds the maximum tenor. Extrapolation beyond TN is not allowed.');
    end

    % Pre-allocate output
    vols = zeros(size(Ks));

    % Optimize for the most common use case: T is a single scalar time
    if isscalar(T)
        
        % --- Case 1: Time is earlier than our first tenor (T <= T1) ---
        if T <= volSurf.Ts(1)
            % Map strikes using moneyness lines: K1 = K * (F1 / F_target)
            K1 = Ks .* (volSurf.fwds(1) / fwd);
            % Eq 12 says variance = var1 * (T/T1). When solving for Vol, it simplifies to Vol = Vol1.
            vols = getSmileVol(volSurf.smiles{1}, K1);
            
        % --- Case 2: Time falls between two tenors (Ti < T <= Ti+1) ---
        else
            % Find the right-side bounding tenor index
            idx_next = find(volSurf.Ts >= T, 1, 'first');
            
            % If T lands exactly on a tenor node, no time interpolation needed!
            if volSurf.Ts(idx_next) == T
                Ki = Ks .* (volSurf.fwds(idx_next) / fwd);
                vols = getSmileVol(volSurf.smiles{idx_next}, Ki);
            else
                % Get the bounding indices and times
                i = idx_next - 1;
                Ti = volSurf.Ts(i);
                Tip1 = volSurf.Ts(i+1);
                
                % Step A: Map the moneyness strikes (Equation 7)
                Ki = Ks .* (volSurf.fwds(i) / fwd);
                Kip1 = Ks .* (volSurf.fwds(i+1) / fwd);
                
                % Step B: Get the raw volatilities from the two adjacent smiles
                Vi = getSmileVol(volSurf.smiles{i}, Ki);
                Vip1 = getSmileVol(volSurf.smiles{i+1}, Kip1);
                
                % Step C: Convert to Total Variance (w = sigma^2 * T)
                Wi = (Vi.^2) .* Ti;
                Wip1 = (Vip1.^2) .* Tip1;
                
                % Step D: Linearly interpolate the variance (Equation 12)
                W_interp = ((Tip1 - T) / (Tip1 - Ti)) .* Wi + ((T - Ti) / (Tip1 - Ti)) .* Wip1;
                
                % Step E: Convert the interpolated variance back to Volatility
                vols = sqrt(W_interp ./ T);
            end
        end
        
    else
        % --- Fallback --- 
        % If your pricer passes an array of T's, you will need a loop here. 
        % (Usually, pricers pass a single T and an array of Ks).
        error('This vectorized implementation expects T to be a scalar.');
    end

end