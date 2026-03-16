% % Inputs :
% f: forward spot for time T, i.e. E[S(T)]
% T: time to expiry of the option
% Ks: vector of strikes
% Vs: vector of implied Black volatilities
% Output :
% u: vector of call options undiscounted prices
function u = getBlackCall(f, T, Ks, Vs)

    if ~(isscalar(f) && isnumeric(f) && isreal(f) && isfinite(f) && f >= 0)
        error('getBlackCall:InvalidForward. f must be a finite non-negative real scalar.');
    end
    if ~(isscalar(T) && isnumeric(T) && isreal(T) && isfinite(T) && T >= 0)
        error('getBlackCall:InvalidMaturity. T must be a finite non-negative real scalar.');
    end
    if ~(isnumeric(Ks) && isreal(Ks) && ~isempty(Ks))
        error('getBlackCall:InvalidStrikes. Ks must be a non-empty real numeric array.');
    end
    if ~(isnumeric(Vs) && isreal(Vs) && ~isempty(Vs))
        error('getBlackCall:InvalidVols. Vs must be a non-empty real numeric array or scalar.');
    end
    if any(~isfinite(Ks(:))) || any(Ks(:) < 0)
        error('getBlackCall:InvalidStrikes. Ks must contain only finite non-negative strikes.');
    end
    if any(~isfinite(Vs(:))) || any(Vs(:) < 0)
        error('getBlackCall:InvalidVols. Vs must contain only finite non-negative volatilities.');
    end
    
    % Calculate d1 and d2
    d1 = (log(f) - log(Ks)) ./ (Vs .* sqrt(T)) + 0.5 * Vs .* sqrt(T);
    d2 = d1 - Vs .* sqrt(T);
    
    % Use the core 'erf' function instead of the toolbox 'normcdf'
    N_d1 = 0.5 * (1 + erf(d1 / sqrt(2)));
    N_d2 = 0.5 * (1 + erf(d2 / sqrt(2)));
    
    % Calculate the undiscounted call price
    u = f .* N_d1 - Ks .* N_d2;
    
    % Edge case where call option with zero strike
    u(Ks == 0) = f;
    
end
