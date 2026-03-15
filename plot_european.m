%% Visualization Script: European Option Prices vs Strike
% Plots call and put prices for several tenors.

% 1. Setup
[spot, lag, days, domdfs, fordfs, vols, cps, deltas] = getMarket();
tau = lag / 365;
Ts = days / 365;

domCurve = makeDepoCurve(Ts, domdfs);
forCurve = makeDepoCurve(Ts, fordfs);
fwdCurve = makeFwdCurve(domCurve, forCurve, spot, tau);
volSurf = makeVolSurface(fwdCurve, Ts, cps, deltas, vols);

% 2. Select tenors: 59D, 365D, 730D
tenor_idx = [5, 8, 10];
colors = {'b', 'r', [0 0.6 0]};

figure('Name', 'European Option Prices', 'Position', [100, 100, 1100, 500]);

% Call prices
subplot(1, 2, 1);
for j = 1:length(tenor_idx)
    idx = tenor_idx(j);
    T = Ts(idx);
    fwd = getFwdSpot(fwdCurve, T);
    K_range = linspace(fwd * 0.7, fwd * 1.3, 100);
    
    [vol_vals, ~] = getVol(volSurf, T, K_range);
    call_prices = getBlackCall(fwd, T, K_range, vol_vals);
    
    plot(K_range, call_prices, '-', 'Color', colors{j}, 'LineWidth', 2); hold on;
    xline(fwd, ':', 'Color', colors{j}, 'HandleVisibility', 'off');
end
title('Undiscounted Call Prices', 'FontSize', 13);
xlabel('Strike (K)');
ylabel('Price');
legend(arrayfun(@(i) sprintf('%d Days', days(i)), tenor_idx, 'UniformOutput', false));
grid on;

% Put prices (via put-call parity)
subplot(1, 2, 2);
for j = 1:length(tenor_idx)
    idx = tenor_idx(j);
    T = Ts(idx);
    fwd = getFwdSpot(fwdCurve, T);
    K_range = linspace(fwd * 0.7, fwd * 1.3, 100);
    
    [vol_vals, ~] = getVol(volSurf, T, K_range);
    call_prices = getBlackCall(fwd, T, K_range, vol_vals);
    put_prices = call_prices - fwd + K_range; % Put-call parity
    
    plot(K_range, put_prices, '-', 'Color', colors{j}, 'LineWidth', 2); hold on;
    xline(fwd, ':', 'Color', colors{j}, 'HandleVisibility', 'off');
end
title('Undiscounted Put Prices', 'FontSize', 13);
xlabel('Strike (K)');
ylabel('Price');
legend(arrayfun(@(i) sprintf('%d Days', days(i)), tenor_idx, 'UniformOutput', false));
grid on;

sgtitle('European Vanilla Option Prices by Tenor', 'FontSize', 15, 'FontWeight', 'bold');
