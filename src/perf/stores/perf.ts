import { defineStore } from 'pinia';
import {
  fetchDeptProgress,
  fetchKpi,
  fetchPerfDistribution,
  fetchPerfList,
  type PerfRow,
} from '../api/perf';

export const usePerfStore = defineStore('perf', {
  state: () => ({
    // filters
    period: '2025 Q3' as string,
    keyword: '' as string,
    dept: '' as string,
    status: '' as string,
    minGrade: '' as string,
    maxGrade: '' as string,

    // sorting & pagination
    sort: 'name' as string, // 'name'|'dept'|'target'|'grade' or '-name' for desc
    page: 1 as number,
    size: 10 as number,

    // table data
    items: [] as PerfRow[],
    total: 0 as number,

    // KPI & charts
    kpi: {
      doneRate: 0,
      avgScore: 0,
      avgGrade: 'B+',
      pending: 0,
      anomaly: 0,
      anomalyRate: 0,
    } as {
      doneRate: number; avgScore: number; avgGrade: string; pending: number; anomaly: number; anomalyRate: number;
    },
    distribution: { bins: [], counts: [] } as { bins: string[]; counts: number[] },
    deptProgress: { labels: [], values: [] } as { labels: string[]; values: number[] },

    // loading flags
    loadingList: false,
    loadingKpi: false,
    loadingCharts: false,
    error: '' as string,
  }),
  actions: {
    async loadList() {
      this.loadingList = true; this.error = '';
      try {
        const data = await fetchPerfList({
          period: this.period,
          dept: this.dept || undefined,
          status: this.status || undefined,
          minGrade: this.minGrade || undefined,
          maxGrade: this.maxGrade || undefined,
          keyword: this.keyword || undefined,
          page: this.page,
          size: this.size,
          sort: this.sort,
        });
        this.items = data.items;
        this.total = data.total;
      } catch (e: any) {
        this.error = e?.message || '列表加载失败';
      } finally {
        this.loadingList = false;
      }
    },
    async loadKpi() {
      this.loadingKpi = true; this.error = '';
      try {
        const data = await fetchKpi({ period: this.period });
        this.kpi = data as any;
      } catch (e: any) {
        this.error = e?.message || 'KPI 加载失败';
      } finally {
        this.loadingKpi = false;
      }
    },
    async loadCharts() {
      this.loadingCharts = true; this.error = '';
      try {
        const [dist, dept] = await Promise.all([
          fetchPerfDistribution({ period: this.period }),
          fetchDeptProgress({ period: this.period }),
        ]);
        this.distribution = dist;
        this.deptProgress = dept;
      } catch (e: any) {
        this.error = e?.message || '图表加载失败';
      } finally {
        this.loadingCharts = false;
      }
    },
    async initLoad() {
      await Promise.all([this.loadKpi(), this.loadCharts(), this.loadList()]);
    },
  },
});
