clear; clc; close all;
sps = [2,4,8,16];
Pe = 10^-6;
M=[2,4,8,16];
for SPS = sps
    SNR_QAM= (qfuncinv(Pe./(2.*(1-1./sqrt(M)))).^2.*((M-1)./3));
    SNR_QAM_ = 10.*log10(SNR_QAM)-10*log10(SPS/2)
end

sps = [2,4,8,16];
M=[2,4,8];
SNR_BPSK = 10*log10(abs(qfuncinv(Pe/2)/2))
for SPS = sps
    SNR = 10.*log10((qfuncinv(Pe./(M-1))./sin(pi./M)).^2);
    SNR_ = SNR-10*log10(SPS)
end
